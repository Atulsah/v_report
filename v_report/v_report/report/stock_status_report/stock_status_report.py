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
	ordered_items_map = get_ordered_items(filters)	

	for i in items:
		op_stock=get_balance_qty_from_slee(i.item_code,filters.from_date)
		ordered_qty = ordered_items_map.get(i.item_code, {}).get("oqty")
		delivered_qty = ordered_items_map.get(i.item_code, {}).get("dqty")
		pending_qty = flt(ordered_qty - delivered_qty) if ordered_qty and ordered_qty > delivered_qty else 0
		closing_stock = get_currents_stock_from_bin(i.item_code)
		remain_qty = flt(pending_qty - closing_stock) if pending_qty else 0
		data.append([0, i.item_name,op_stock, "production_qty", ordered_qty,delivered_qty, pending_qty, closing_stock, remain_qty])

	return data

def dispatched_item_report(filters):
	data = []
	items = get_items(filters)
	sub_items = get_sub_itemss(filters)
	ordered_items_map = get_ordered_items(filters)	
	sub_items_map = get_sub_items_data(items,ordered_items_map)
	for i in sub_items:
		s_item_name = i.item_name
		s_op_stock = get_balance_qty_from_slee(i.item_code,filters.from_date)
		s_ordered_qty = sub_items_map.get(i.item_code, {}).get("oqty")
		s_delivered_qty = sub_items_map.get(i.item_code, {}).get("dqty")
		s_pending_qty = flt(s_ordered_qty - s_delivered_qty) if s_ordered_qty and s_ordered_qty > s_delivered_qty else 0
		s_closing_stock = get_currents_stock_from_bin(i.item_code)
		s_remain_qty = flt(s_pending_qty - s_closing_stock) if s_pending_qty else 0
		data.append([1, s_item_name,s_op_stock,"production_qty", s_ordered_qty,s_delivered_qty, s_pending_qty, s_closing_stock, s_remain_qty])
	
	return data

def mixed_report(filters):
	data = []
	items = get_items(filters)
	ordered_items_map = get_ordered_items(filters)	
	for i in items:
		ordered_qty = ordered_items_map.get(i.item_code, {}).get("oqty")
		delivered_qty = ordered_items_map.get(i.item_code, {}).get("dqty")
		pending_qty = flt(ordered_qty - delivered_qty) if ordered_qty and ordered_qty > delivered_qty else 0
		closing_stock = get_currents_stock_from_bin(i.item_code)
		op_stock = get_balance_qty_from_slee(i.item_code,filters.from_date)
		remain_qty = flt(pending_qty - closing_stock) if pending_qty else 0
		data.append([0, i.item_name,op_stock, "production_qty", ordered_qty,delivered_qty, pending_qty, closing_stock, remain_qty])
		sub_items = get_sub_items(i.item_code)
		for j in sub_items:
			s_op_stock=get_balance_qty_from_slee(j.item_code,filters.from_date)
			s_ordered_qty = flt(ordered_qty * j.qty) if j.qty and ordered_qty else 0
			s_delivered_qty = flt(delivered_qty * j.qty) if j.qty and delivered_qty else 0
			s_pending_qty = flt(s_ordered_qty - s_delivered_qty)if s_ordered_qty and s_ordered_qty > s_delivered_qty else 0
			s_closing_stock = get_currents_stock_from_bin(j.item_code)
			s_remain_qty = flt(s_pending_qty - s_closing_stock) if s_pending_qty else 0
			data.append([1, j.item_name,s_op_stock, "production_qty", s_ordered_qty,s_delivered_qty, s_pending_qty, s_closing_stock, s_remain_qty])
	
	return data

def get_items(filters):
	return frappe.db.sql("""select item.item_code, item.item_name from `tabItem` item where item.disabled=0 and item.pch_pallet_size >=1 and item.buyer=%(buyer)s """,{'buyer': filters.foreign_buyer},as_dict=1)

def get_ordered_items(filters):
	ordered_items = frappe.db.sql("""
		select 
			so.name,so_item.item_code as item_code,
			ifnull(sum(so_item.qty),0) as ordered_qty,
			ifnull(sum(so_item.delivered_qty),0) as delivered_qty 
		from 
			`tabSales Order Item` so_item,`tabSales Order` so 
		where 
			so.transaction_date BETWEEN %(from_date)s and %(to_date)s 
			and so.company=%(company)s and so_item.parent=so.name and so.docstatus=1 
		group by 
			so_item.item_code""",
			{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company},
		as_dict=1) 
	ordered_items_map = {}
	for d in ordered_items:
		ordered_items_map.setdefault(d.item_code, frappe._dict())
		ordered_items_map[d.item_code]["oqty"] = flt(d.ordered_qty)
		ordered_items_map[d.item_code]["dqty"]  = flt(d.delivered_qty)

	return ordered_items_map	

def get_dispatched_items(filters):
	ordered_items = frappe.db.sql("""
		select 
			so.name,so_item.item_code as item_code,
			ifnull(sum(so_item.qty),0) as ordered_qty,
			ifnull(sum(so_item.delivered_qty),0) as delivered_qty 
		from 
			`tabSales Order Item` so_item,`tabSales Order` so 
		where 
			so.transaction_date BETWEEN %(from_date)s and %(to_date)s 
			and so.company=%(company)s and so_item.parent=so.name 
			and so.docstatus=1 
		group by 
			so_item.item_code""",
			{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company},
		as_dict=1) 
	ordered_items_map = {}
	for d in ordered_items:
		ordered_items_map.setdefault(d.item_code, frappe._dict())
		ordered_items_map[d.item_code]["oqty"] = flt(d.ordered_qty)
		ordered_items_map[d.item_code]["dqty"]  = flt(d.delivered_qty)

	return ordered_items_map	

def get_sub_items(item_code):
	return frappe.db.sql("""select bom.item,bom_item.item_code,bom_item.item_name,bom_item.qty,bom_item.uom from `tabBOM Item` bom_item,`tabBOM` bom where bom_item.parent=bom.name and bom.item = %s """,(item_code),as_dict=1)
	#return frappe.db.sql("""
	#	select 
	#		pb.new_item_code,pbi.item_code,pbi.item_name,pbi.qty,pbi.uom 
	# 	from 
	#		`tabProduct Bundle Item` pbi,`tabProduct Bundle` pb 
	#	where 
	#		pbi.parent=pb.name and pb.new_item_code = %s """,(item_code),as_dict=1)

def get_currents_stock_from_bin(item_code):
	item_stock_qty = frappe.db.sql("""
		select 
			ifnull(actual_qty,0) as actual_qty 
		from 
			`tabBin` 
		where 
			item_code = %s order by creation Desc limit 1""",
			(item_code),as_dict=1)
	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0

#Columns in report
def get_columns():
	columns = [{
		"fieldname": "flag",
		"label": _(" "),
		"fieldtype": "data",
		"width": 10
	}]
	columns.append({
		"fieldname": "item_name",
		"label": _("Items"),
		"fieldtype": "data",
		"width": 300
	})
	columns.append({
		"fieldname": "opening_stock",
		"label": _("Opening Stock"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "production_qty",
		"label": _("Production Qty"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "order_received",
		"label": _("Order Received"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "dispatched_qty",
		"label": _("Dispatched Qty"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "pending_qty",
		"label": _("Pending Qty"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "closing_stock",
		"label": _("Closing Stock"),
		"fieldtype": "Data",
		"width": 120
	})
	columns.append({
		"fieldname": "Product Remains",
		"label": _("product_remains"),
		"fieldtype": "Data",
		"width": 120
	})

	return columns	

def get_balance_qty_from_slee(item_code,posting_date):
	balance_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry`
		where item_code=%s and posting_date < %s and is_cancelled='No'
		order by posting_date desc, posting_time desc, name desc
		limit 1""", (item_code, posting_date))

	return flt(balance_qty[0][0]) if balance_qty else 0.0

def get_in_qty(item_code, starting_date, ending_date):
	in_qty = frappe.db.sql("""
		select 
			sle.item_code, sle.posting_date, sle.actual_qty, 
			sle.company, sle.voucher_type, sle.qty_after_transaction,
		from 
			`tabStock Ledger Entry` sle ,`tabStock Entry` se
		where 
			item_code=%s and posting_date BETWEEN %s and %s and is_cancelled='No'
			and so_item.parent=so.name and so_item.parent=so.name
		order by 
			posting_date desc, posting_time desc, name desc
		limit 1""", (item_code, starting_date, ending_date)) 

def get_sub_items_data(items,ordered_items_map):
	sub_item_map = {}
	for i in items:
		sub_item = get_sub_items(i.item_code)
		for j in sub_item:
			sub_item_map.setdefault(j.item_code, frappe._dict())
			#sub_item_map[j.item_code]["name"] = j.item_name
			sub_item_map[j.item_code]["oqty"] = flt(j.qty * ordered_items_map.get(i.item_code, {}).get("oqty")) if (ordered_items_map.get(i.item_code, {}).get("oqty")) and j.qty else 0
			sub_item_map[j.item_code]["dqty"] = flt(j.qty * ordered_items_map.get(i.item_code, {}).get("dqty")) if (ordered_items_map.get(i.item_code, {}).get("dqty")) and j.qty  else 0

		
	return sub_item_map

def get_sub_itemss(filters):
		return frappe.db.sql("""
			select 
				item.item_code, item.item_name 
			from 
				`tabItem` item 
			where 
				item.disabled=0 and item.pch_pallet_size <=0 and item.buyer=%(buyer)s """,
				{'buyer': filters.foreign_buyer},as_dict=1)