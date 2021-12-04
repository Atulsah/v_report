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
	bundled_count = get_max_bundled_items()
	for i in items:
		stock_qty = get_current_stock_from_bin(i.item_code)
		required_qty = round((i.ordered_qty - i.delivered_qty),2) if round((i.ordered_qty - i.delivered_qty),2) >=1 else 0

		row = [i.foreign_buyer_name,i.item_code,i.item_name,i.ordered_qty,i.delivered_qty,stock_qty,required_qty]
		if frappe.db.exists('Product Bundle',i.item_code):
			bundled = frappe.get_doc('Product Bundle', i.item_code)
			counter = 0
			for b in bundled.get('items'):
				counter += 1
				r_qty = flt(b.qty * required_qty)
				b_stock = get_current_stock_from_bin(b.item_code)
				to_mfg  = flt(r_qty - b_stock) if flt(r_qty - b_stock) >= 1 else 0.0
				item_name = frappe.db.get_value("Item",{"name": b.item_code}, "item_name")
				row += [item_name,b_stock,r_qty,to_mfg]
				for x in range(counter+1,bundled_count):
					for x in range(counter+1,bundled_count):
						row += ['',0.0,0.0,0.0]
		else:
			for x in range(1,bundled_count):
				row += ['',0.0,0.0,0.0]

   
    
	
	data.append(row)
	return columns, data


def get_item_conditions(filters):
	conditions = []
	if filters.get("item_group"):
		conditions.append("so_item.item_group=%(item_group)s")  
	if filters.get("foreign_buyer_name"):
		conditions.append("so.foreign_buyer_name=%(foreign_buyer_name)s")       
	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_ordered_items(filters):
	return frappe.db.sql("""select so.foreign_buyer_name,so_item.item_code,so_item.item_name,sum(so_item.qty) as ordered_qty,sum(so_item.delivered_qty) as delivered_qty from `tabSales Order Item` so_item,`tabSales Order` so where so.transaction_date BETWEEN %(from_date)s and %(to_date)s and so.company=%(company)s and so_item.parent=so.name and so.docstatus=1 {itm_conditions} group by so_item.item_code,so.foreign_buyer_name order by so.transaction_date Desc,so_item.item_code Asc """.format(itm_conditions=get_item_conditions(filters)),{'from_date':filters.from_date,'to_date':filters.to_date,'company':filters.company,'item_group': filters.item_group,'foreign_buyer_name': filters.foreign_buyer_name},as_dict=1) 


def get_current_stock_from_bin(item_code):
	stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	if stock_qty and stock_qty[0].actual_qty > 0:
		return stock_qty[0].actual_qty
	else:
		return 0

def get_max_bundled_items():
	cnt = frappe.db.sql("""select max(idx) as count from `tabProduct Bundle Item`""",as_dict=1)
	if cnt and cnt[0].count > 0:
		return int(cnt[0].count+1)
	else:
		return int(2)   

#Add columns in report
def get_columns():
	"""return columns based on filters"""
	bundled_count = get_max_bundled_items()
	columns = [{
		"fieldname": "buyer",
		"label": _("Foreign Buyer"),
		"fieldtype": "Link",
		"options": "Customer",
		"width": 120

	}]
	columns.append({
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 100
	})      
	columns.append({
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 180
	})      
	columns.append({
		"fieldname": "ordered",
		"label": _("Ordered Qty"),
		"fieldtype": "Float",
		"width": 100
	})      
	columns.append({
		"fieldname": "delivered",
		"label": _("Delivered Qty"),
		"fieldtype": "Float",
		"width": 100
	})
	columns.append({
		"fieldname": "stock",
		"label": _("Stock Qty"),
		"fieldtype": "Float",
		"width": 100
	})      
	columns.append({
		"fieldname": "required",
		"label": _("Required Qty"),
		"fieldtype": "Float",
		"width": 100
	})
	for x in range(1,bundled_count):
		columns.append({
			"fieldname": frappe.scrub("bundled_item_"+str(x)),
			"label": "Bundled Item "+str(x),
			"fieldtype": "Data",
			"width": 160
		})
		columns.append({
			"fieldname": frappe.scrub("bundled_stock_"+str(x)),
			"label": "Stock Qty "+str(x),
			"fieldtype": "Float",
			"width": 90
		})
		columns.append({
			"fieldname": frappe.scrub("bundled_qty_"+str(x)),
			"label": "Req. qty "+str(x),
			"fieldtype": "Float",
			"width": 90
		})
		columns.append({
			"fieldname": frappe.scrub("tomfg_qty_"+str(x)),
			"label": "To Mfg Qty "+str(x),
			"fieldtype": "Float",
			"width": 90
		})


	return columns
