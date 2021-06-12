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


def execute(filters=None):
	columns = get_columns() 
	data = []
	items = get_ordered_items(filters)
	item_stock_map = {}
	for i in items:
		data.append([i.posting_date,i.t_warehouse,i.item_code,i.item_name,i.qty,i.weight_qty])
	return columns, data


def get_item_conditions(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("mr_item.item_code=%(item_code)s")	

	if filters.get("warehouse"):
		conditions.append("mr_item.t_warehouse=%(warehouse)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_ordered_items(filters):
 	return frappe.db.sql("""select mr.posting_date,mr_item.t_warehouse,mr_item.item_code,mr_item.item_name,mr_item.qty,mr_item.weight_qty from `tabStock Entry` mr, `tabStock Entry Detail` mr_item where mr.posting_date BETWEEN %(from_date)s and %(to_date)s and mr.stock_entry_type="Material Receipt" and mr_item.parent=mr.name and company=%(company)s and mr.docstatus=1 {itm_conditions} order by mr.posting_date Asc """.format(itm_conditions=get_item_conditions(filters)), {'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company, 'item_code': filters.item_code,'warehouse': filters.warehouse},as_dict=1) 

#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "posting_date",
		"label": _("Received Date"),  
		"fieldtype": "Date",
		"width": 100
	}]
	columns.append({
		"fieldname": "t_warehouse",
		"label": _("Warehouse"),
		"fieldtype": "Link",
		"options": "Warehouse", 
		"width": 180
	})
	columns.append({
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 200
	})	
	columns.append({
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 280
	})		
	columns.append({
		"fieldname": "qty",
		"label": _("Qty in Pcs"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})
	columns.append({
		"fieldname": "stock_weight",
		"label": _("Qty in Weight"),
		"fieldtype": "Float",
		"width": 100,
		"precision": 2
	})
	return columns				