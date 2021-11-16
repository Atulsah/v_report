
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
# import frappe

def execute(filters=None):
	columns = get_columns() 
	data = []
	items = get_ordered_items(filters)
	item_stock_map = {}
	for i in items:
		weight_per_unit = frappe.db.get_value("Item", {'name': i.item_code}, "weight_per_unit")
		stock_qty = get_current_stock_from_bin(i.item_code)
		pending_qty = round(i.qty-i.delivered_qty,2) if i.delivered_qty > 0 else i.qty
		pending_wt = round(pending_qty * weight_per_unit, 2)
		if stock_qty > pending_qty:
			if i.item_code in item_stock_map:
				item_stock_map[i.item_code]= flt(item_stock_map[i.item_code]+pending_qty)
				if stock_qty > item_stock_map[i.item_code]:
					available_qty = pending_qty
				else:
					available_qty = flt(stock_qty -(item_stock_map[i.item_code]-pending_qty))	
			else:
				item_stock_map[i.item_code]= pending_qty
				available_qty = pending_qty						

		else:
			available_qty = stock_qty	if stock_qty else 0

		required_qty = round(i.qty - (i.delivered_qty + available_qty),2)

		if i.delivered_qty > i.qty:
			available_qty,required_qty,pending_qty,pending_wt = 0,0,0,0
	

		data.append([i.customer,i.foreign_buyer_name,i.final_destination,i.item_code,i.item_name,i.p_o_no,i.p_o_date,i.name,i.delivery_date,i.qty,i.delivered_qty,pending_qty,pending_wt,available_qty,required_qty,i.weight_per_unit,i.pch_pallet_size])
	return columns, data

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_group"):
		conditions.append("so_item.item_group=%(item_group)s")	

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_ordered_items(filters):
	return frappe.db.sql("""select so.customer,so.foreign_buyer_name,so.final_destination,so.name,so_item.item_code,so_item.item_name,so_item.p_o_no,so_item.p_o_date,so_item.qty,so_item.delivered_qty,so_item.delivery_date,so_item.weight_per_unit,so_item.pch_pallet_size from `tabSales Order Item` so_item,`tabSales Order` so where so.transaction_date BETWEEN %(from_date)s and %(to_date)s and so.company=%(company)s and so_item.parent=so.name  and so_item.pch_pallet_size >=1 and so.docstatus=1 {itm_conditions} order by so.delivery_date Asc """.format(itm_conditions=get_item_conditions(filters)),{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company,'item_group': filters.item_group},as_dict=1) 

def get_current_stock_from_bin(item_code):
	stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	if stock_qty and stock_qty[0].actual_qty > 0:
		return stock_qty[0].actual_qty
	else:
		return 0

#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "customer",
		"label": _("Customer"),  
		"fieldtype": "Link",
		"options": "Customer",
		"width": 150

	}]
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
		"fieldname": "sales_order",
		"label": _("Sales Order"),
		"fieldtype": "Link",
		"options": "Sales Order",
		"width": 75
	})
	columns.append({
		"fieldname": "delivery_date",
		"label": _("Delivery Date"),
		"fieldtype": "Date",
		"width": 75,
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
		"label": _("P. Weight"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "stock_qty",
		"label": _("Stock"),
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
		"fieldname": "weight_per_unit",
		"label": _("Weight Per Unit"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pcs_per_crate",
		"label": _("Pcs/Set per Crate"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	return columns				