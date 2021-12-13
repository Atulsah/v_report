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
	
	if filters.report_type == "Mixed-Report":
		data = []
		data = mixed_report(filters)

	elif filters.report_type == "Dispatched-Item-Report":
		data = []
		data = dispatched_item_report(filters)

	else:
		data = [] 
		data = ordered_item_report(filters)

	
	return columns, data

def ordered_item_report(filters):
	data = []
	items = get_items(filters)
	#order_items = get_ordered_items(filters)
	# #sle = get_stock_ledger_entries(filters, items)
	#item_details_map = get_item_details(filters)
	#if not sle:
	#	return columns, []
	#iwb_map = get_item_warehouse_map(filters, sle)	
	ordered_items_map = get_ordered_items(filters)	

	
	for i in items:
		ordered_qty = ordered_items_map.get(i.item_code, {}).get("oqty")
		delivered_qty = ordered_items_map.get(i.item_code, {}).get("dqty")
		pending_qty = ordered_qty - delivered_qty
		data.append(["opening_stock", "production_qty", ordered_qty,delivered_qty, pending_qty, "closing_stock", "product_remains", i.item_name])

	return data

def dispatched_item_report(filters):
	data = []
	
	data.append(["opening_stock", "production_qty", "order_received", "dispatched_qty", "pending_qty", "closing_stock", "product_remains", "item_name"])

	return data

def mixed_report(filters):
	data = []
	
	data.append(["opening_stock", "production_qty", "order_received", "dispatched_qty", "pending_qty", "closing_stock", "product_remains", "item_name"])

	return data

def get_items(filters):
	return frappe.db.sql("""select item.item_code, item.item_name from `tabItem` item where item.disabled=0 and item.pch_pallet_size >=1 and item.buyer=%(buyer)s """,{'buyer': filters.foreign_buyer},as_dict=1)

def get_ordered_items(filters):
	ordered_items = frappe.db.sql("""select so.name,so_item.item_code as item_code,ifnull(sum(so_item.qty),0) as ordered_qty,ifnull(sum(so_item.delivered_qty),0) as delivered_qty from `tabSales Order Item` so_item,`tabSales Order` so where so.transaction_date BETWEEN %(from_date)s and %(to_date)s and so.company=%(company)s and so_item.parent=so.name and so.docstatus=1 group by so_item.item_code""",{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company},as_dict=1) 
	ordered_items_map = {}
	for d in ordered_items:
		ordered_items_map.setdefault(d.item_code, frappe._dict())
		ordered_items_map[d.item_code]["oqty"] = flt(d.ordered_qty)
		ordered_items_map[d.item_code]["dqty"]  = flt(d.delivered_qty)

	return ordered_items_map	
def get_sub_items(item_code):
	return frappe.db.sql("""select bom.item,bom_item.item_code,bom_item.item_name,bom_item.qty,bom_item.uom from `tabBOM Item` bom_item,`tabBOM` bom where bom_item.parent=bom.name and bom.item = %s """,(item_code),as_dict=1)

def get_currents_stock_from_bin(item_code):
	item_stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0


#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "opening_stock",
		"label": _("Opening Stock"),
		"fieldtype": "Data",
		"width": 125
	}]
	columns.append({
		"fieldname": "production_qty",
		"label": _("Production Qty"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "order_received",
		"label": _("Order Received"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "dispatched_qty",
		"label": _("Dispatched Qty"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "pending_qty",
		"label": _("Pending Qty"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "closing_stock",
		"label": _("Closing Stock"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "Product Remains",
		"label": _("product_remains"),
		"fieldtype": "Data",
		"width": 125
	})
	columns.append({
		"fieldname": "item_name",
		"label": _("Items"),
		"fieldtype": "data",
		"width": 325
	})
	return columns	

