# Copyright (c) 2013, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe import utils
from frappe.utils import flt
from datetime import datetime,timedelta,date
from frappe.utils import getdate, date_diff,add_days, add_years, cstr,formatdate, strip


def execute(filters):
	columns = get_columns() 
	
	if filters.report_type == "Complete-Report":
		data = []
		data = complete_report(filters)

	elif filters.report_type == "Dispatched-Item-Report":
		data = []
		data = dispatched_item_report(filters)

	else:
		data = [] 
		data = ordered_item_report(filters)

	
	return columns, data

def dispatched_item_report(filters):
	data = []
	items = get_ordered_items(filters)
	sub_item_stock_map = {}
	sub_item_pending_map = {}

	for i in items:
		pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty
		bom_items = get_sub_items(i.item_code)
		for j in bom_items:
			sub_item_qty = i.qty * j.qty
			sub_item_dlvr_qty = i.delivered_qty * j.qty
			sub_item_weight_per_unit = frappe.db.get_value("Item", {'name': j.item_code}, "weight_per_unit")
			sub_item_weight_uom = frappe.db.get_value("Item", {'name': j.item_code}, "weight_uom")
			sub_item_stock_map[j.item_code] = get_current_stock_from_bin(j.item_code) if j.item_code not in sub_item_stock_map else sub_item_stock_map[j.item_code]
			sub_item_pending_qty = round(pending_qty * j.qty,2) if sub_item_dlvr_qty > 0 else sub_item_qty
			sub_item_pending_weight = round(sub_item_pending_qty * sub_item_weight_per_unit, 2)
			sub_item_pending_map[j.item_code] = 0 if j.item_code not in sub_item_pending_map else sub_item_pending_map[j.item_code]
			sub_item_stock_qty = sub_item_stock_map[j.item_code]
			sub_item_stock_qty_wt = 0 if sub_item_stock_qty <=0 else round(sub_item_stock_qty * sub_item_weight_per_unit, 2)
			sub_item_crate_size = round(i.pch_pallet_size * j.qty,2)
		
			if sub_item_stock_qty >= sub_item_pending_qty:
				sub_item_stock_qty = 0 if sub_item_stock_qty <=sub_item_pending_qty else sub_item_stock_qty
				sub_item_required_qty = (sub_item_pending_qty - sub_item_stock_map[j.item_code]) if (sub_item_pending_qty <= sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]+sub_item_pending_qty
				sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - sub_item_pending_qty
				sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + sub_item_pending_qty
			else:
				sub_item_stock_qty = 0 if sub_item_stock_qty <=0 else sub_item_stock_qty
				sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + (sub_item_pending_qty if sub_item_stock_qty <= 0 else (sub_item_pending_qty - sub_item_stock_qty))
				sub_item_required_qty = (sub_item_pending_qty - sub_item_stock_map[j.item_code]) if (sub_item_pending_qty < sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]
				sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - sub_item_pending_qty
						


			if sub_item_dlvr_qty > sub_item_qty:
				sub_item_required_qty,sub_item_pending_qty,pending_wt = 0,0,0


			data.append([i.name,i.delivery_date,i.customer,i.foreign_buyer_name,i.final_destination,i.p_o_no,i.p_o_date,j.item_code,j.item_name,sub_item_weight_per_unit,sub_item_weight_uom,sub_item_qty,sub_item_dlvr_qty,sub_item_pending_qty,sub_item_pending_weight,sub_item_stock_qty,sub_item_stock_qty_wt,sub_item_required_qty,sub_item_crate_size])	
	return data

def complete_report(filters):
	data = []
	items = get_ordered_items(filters)
	#item_stock_map = {}
	item_pending_stock_map = {}
	item_current_stock_map = {}
	sub_item_stock_map = {}
	sub_item_pending_map = {}

	for i in items:
		weight_per_unit = frappe.db.get_value("Item", {'name': i.item_code}, "weight_per_unit")
		item_weight_uom = frappe.db.get_value("Item", {'name': i.item_code}, "weight_uom")
		#stock_qty = get_current_stock_from_bin(i.item_code)
		item_current_stock_map[i.item_code] = get_current_stock_from_bin(i.item_code) if i.item_code not in item_current_stock_map else item_current_stock_map[i.item_code]
		pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty
		pending_wt = round(pending_qty * weight_per_unit, 2)
		item_pending_stock_map[i.item_code] = 0 if i.item_code not in item_pending_stock_map else item_pending_stock_map[i.item_code]
		current_stock_qty = item_current_stock_map[i.item_code]
		stock_qty_wt = 0 if current_stock_qty <=0 else round(current_stock_qty * weight_per_unit, 2)
		current_pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty

		if current_stock_qty >= current_pending_qty:
			current_stock_qty = 0 if current_stock_qty <=current_pending_qty else current_stock_qty
			required_quantity = 0 if (current_pending_qty <= item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]+current_pending_qty
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + current_pending_qty
		else:
			current_stock_qty = 0 if current_stock_qty <=0 else current_stock_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + (current_pending_qty if current_stock_qty <= 0 else (current_pending_qty - current_stock_qty))
			required_quantity = 0 if (current_pending_qty < item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty


		if i.delivered_qty > i.qty:
			pending_qty,pending_wt = 0,0,0,0


		data.append([i.name,i.delivery_date,i.customer,i.foreign_buyer_name,i.final_destination,i.p_o_no,i.p_o_date,i.item_code,i.item_name,i.weight_per_unit,item_weight_uom,i.qty,i.delivered_qty,current_pending_qty,pending_wt,current_stock_qty,stock_qty_wt,required_quantity,i.pch_pallet_size])
	
		pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty
		bom_items = get_sub_items(i.item_code)
		for j in bom_items:
			sub_item_qty = i.qty * j.qty
			sub_item_dlvr_qty = i.delivered_qty * j.qty
			sub_item_weight_per_unit = frappe.db.get_value("Item", {'name': j.item_code}, "weight_per_unit")
			sub_item_weight_uom = frappe.db.get_value("Item", {'name': j.item_code}, "weight_uom")
			sub_item_stock_map[j.item_code] = get_current_stock_from_bin(j.item_code) if j.item_code not in sub_item_stock_map else sub_item_stock_map[j.item_code]
			sub_item_pending_qty = round(pending_qty * j.qty,2) if sub_item_dlvr_qty > 0 else sub_item_qty
			sub_item_pending_weight = round(sub_item_pending_qty * sub_item_weight_per_unit, 2)
			sub_item_pending_map[j.item_code] = 0 if j.item_code not in sub_item_pending_map else sub_item_pending_map[j.item_code]
			sub_item_stock_qty = sub_item_stock_map[j.item_code]
			sub_item_stock_qty_wt = 0 if sub_item_stock_qty <=0 else round(sub_item_stock_qty * sub_item_weight_per_unit, 2)
			sub_item_crate_size = round(i.pch_pallet_size * j.qty,2)

			if sub_item_stock_qty >= sub_item_pending_qty:
				sub_item_stock_qty = 0 if sub_item_stock_qty <=sub_item_pending_qty else sub_item_stock_qty
				sub_item_required_qty = (sub_item_pending_qty - sub_item_stock_map[j.item_code]) if (sub_item_pending_qty <= sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]+sub_item_pending_qty
				sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - sub_item_pending_qty
				sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + sub_item_pending_qty
			else:
				sub_item_stock_qty = 0 if sub_item_stock_qty <=0 else sub_item_stock_qty
				sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + (sub_item_pending_qty if sub_item_stock_qty <= 0 else (sub_item_pending_qty - sub_item_stock_qty))
				sub_item_required_qty = (sub_item_pending_qty - sub_item_stock_map[j.item_code]) if (sub_item_pending_qty < sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]
				sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - sub_item_pending_qty
						


			if sub_item_dlvr_qty > sub_item_qty:
				sub_item_required_qty,sub_item_pending_qty,pending_wt = 0,0,0


			data.append([i.name,i.delivery_date,"  ","  ","  ",j.p_o_no,j.p_o_date,j.item_code,j.item_name,sub_item_weight_per_unit,sub_item_weight_uom,sub_item_qty,sub_item_dlvr_qty,sub_item_pending_qty,sub_item_pending_weight,sub_item_stock_qty,sub_item_stock_qty_wt,sub_item_required_qty,sub_item_crate_size])	
		
		
	return data

def ordered_item_report(filters):
	data = []
	items = get_ordered_items(filters)
	item_pending_stock_map = {}
	item_current_stock_map = {}
	for i in items:
		weight_per_unit = frappe.db.get_value("Item", {'name': i.item_code}, "weight_per_unit")
		item_weight_uom = frappe.db.get_value("Item", {'name': i.item_code}, "weight_uom")
		item_current_stock_map[i.item_code] = get_current_stock_from_bin(i.item_code) if i.item_code not in item_current_stock_map else item_current_stock_map[i.item_code]
		pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty
		pending_wt = round(pending_qty * weight_per_unit, 2)
		item_pending_stock_map[i.item_code] = 0 if i.item_code not in item_pending_stock_map else item_pending_stock_map[i.item_code]
		current_stock_qty = item_current_stock_map[i.item_code]
		stock_qty_wt = round(current_stock_qty * weight_per_unit, 2)
		current_pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty

		if current_stock_qty >= current_pending_qty:
			current_stock_qty = 0 if current_stock_qty <=current_pending_qty else current_stock_qty
			required_quantity = 0 if (current_pending_qty <= item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]+current_pending_qty
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + current_pending_qty
		else:
			current_stock_qty = 0 if current_stock_qty <=0 else current_stock_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + (current_pending_qty if current_stock_qty <= 0 else (current_pending_qty - current_stock_qty))
			required_quantity = 0 if (current_pending_qty < item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty


		if i.delivered_qty > i.qty:
			pending_qty,pending_wt = 0,0,0,0
	

		data.append([i.name,i.delivery_date,i.customer,i.foreign_buyer_name,i.final_destination,i.p_o_no,i.p_o_date,i.item_code,i.item_name,i.weight_per_unit,item_weight_uom,i.qty,i.delivered_qty,current_pending_qty,pending_wt,current_stock_qty,stock_qty_wt,required_quantity,i.pch_pallet_size])
	return data

#section close

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_group"):
		conditions.append("so_item.item_group=%(item_group)s")	

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_ordered_items(filters):
	return frappe.db.sql("""select so.customer,so.foreign_buyer_name,so.final_destination,so_item.p_o_no,so_item.p_o_date,so.name,so_item.item_code,so_item.item_name,so_item.uom,so_item.qty,so_item.delivered_qty,so_item.delivery_date,so_item.weight_per_unit,so_item.pch_pallet_size from `tabSales Order Item` so_item,`tabSales Order` so where so.transaction_date BETWEEN %(from_date)s and %(to_date)s and so.company=%(company)s and so_item.parent=so.name  and so_item.pch_pallet_size >=1 and so.docstatus=1 {itm_conditions} order by so.delivery_date Asc """.format(itm_conditions=get_item_conditions(filters)),{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company,'item_group': filters.item_group},as_dict=1) 

def get_sub_items(item_code):
	return frappe.db.sql("""select bom.item,bom_item.item_code,bom_item.item_name,bom_item.qty,bom_item.uom from `tabBOM Item` bom_item,`tabBOM` bom where bom_item.parent=bom.name and bom.item = %s """,(item_code),as_dict=1)

def get_current_stock_from_bin(item_code):
	item_stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0


#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "sales_order",
		"label": _("Sales Order"),
		"fieldtype": "Link",
		"options": "Sales Order",
		"width": 75
	}]
	columns.append({
		"fieldname": "delivery_date",
		"label": _("Delivery Date"),
		"fieldtype": "Date",
		"width": 75,
	})
	columns.append({
		"fieldname": "customer",
		"label": _("Customer"),  
		"fieldtype": "Link",
		"options": "Customer",
		"width": 150
	})
	columns.append({
		"fieldname": "foreign_buyer_name",
		"label": _("Buyer"),
		"fieldtype": "Data",
		"width": 75
	})
	columns.append({
		"fieldname": "final_destination",
		"label": _("Destination"),
		"fieldtype": "Data",
		"width": 75
	})
	columns.append({
		"fieldname": "p_o_no",
		"label": _("PO No"),
		"fieldtype": "Data",
		"width": 60
	})
	columns.append({
		"fieldname": "p_o_date",
		"label": _("Date"),
		"fieldtype": "Date",
		"width": 60
	})
	columns.append({
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 75
	})	
	columns.append({
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 100
	})
	columns.append({
		"fieldname": "weight_per_unit",
		"label": _("Unit Weight"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "uom",
		"label": _("UOM"),
		"fieldtype": "Data",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "order_qty",
		"label": _("P.O Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})	
	columns.append({
		"fieldname": "delivered_qty",
		"label": _("Dlvrd Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pending_qty",
		"label": _("Pending Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pending_wt",
		"label": _("Pending Qty Wt"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "item_stock_qty",
		"label": _("Stock"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "stock_qty_wt",
		"label": _("Stock Qty Wt   "),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "required_qty",
		"label": _("Required"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pcs_per_crate",
		"label": _("Crate Size"),
		"fieldtype": "data",
		"width": 75,
		"precision": 2
	})
	return columns	