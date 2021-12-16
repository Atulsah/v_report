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
		stock_qty = get_current_stock_from_bin(i.item_code)
		received_quantity = i.received_qty - i.returned_qty
		pending_delivery = i.qty - received_quantity
		data.append([i.supplier,i.item_code,i.item_name,i.item_specification,i.name,i.transaction_date,i.qty,i.stock_uom,i.rate,received_quantity,pending_delivery,stock_qty,i.warehouse])
	return columns, data

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_group"):
		conditions.append("so_item.item_group=%(item_group)s")	

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_ordered_items(filters):
	return frappe.db.sql("""select po.supplier,po_item.item_code,po_item.item_name,po_item.item_specification,po.name,po.transaction_date,po_item.stock_uom,po_item.qty,po_item.rate,po_item.warehouse,po_item.received_qty,po_item.returned_qty from `tabPurchase Order Item` po_item,`tabPurchase Order` po where po.schedule_date BETWEEN %(from_date)s and %(to_date)s and po.company=%(company)s and po_item.parent=po.name and po.docstatus=1 {itm_conditions} order by po.schedule_date Asc """.format(itm_conditions=get_item_conditions(filters)),{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company,'item_group': filters.item_group},as_dict=1) 


def get_current_stock_from_bin(item_code):
	stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	if stock_qty and stock_qty[0].actual_qty > 0:
		return stock_qty[0].actual_qty
	else:
		return 0

#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "supplier",
		"label": _("Supplier"),  
		"fieldtype": "Link",
		"options": "Supplier",
		"width": 100

	}]
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
		"fieldname": "item_specification",
		"label": _("Specification"),
		"fieldtype": "Data",
		"width": 100
	})	
	columns.append({
		"fieldname": "purchase_order",
		"label": _("Purchase Order"),
		"fieldtype": "Link",
		"options": "Purchase Order",
		"width": 100
	})
	columns.append({
		"fieldname": "transaction_date",
		"label": _("Date"),
		"fieldtype": "Date",
		"width": 100
	})
	columns.append({
		"fieldname": "qty",
		"label": _("Purchase Qty"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})
	columns.append({
		"fieldname": "stock_uom",
		"label": _("UOM"),
		"fieldtype": "Data",
		"width": 50
	})
	columns.append({
		"fieldname": "rate",
		"label": _("Rate"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "received_quantity",
		"label": _("Receive Qty"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})
	columns.append({
		"fieldname": "pending_delivery",
		"label": _("Pending Qty"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})	
	columns.append({
		"fieldname": "stock_qty",
		"label": _("Stock"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})
	columns.append({
		"fieldname": "warehouse",
		"label": _("Warehouse"),
		"fieldtype": "Link",
		"options": "Warehouse",
		"width": 100
	})
	return columns				