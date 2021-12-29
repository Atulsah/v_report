# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.stock_ledger import get_previous_sle, NegativeStockError

class RaisedEquipmentIssue(Document):


	def on_submit(self):
		self.create_stock_entry()


	def create_stock_entry(doc):
		se = frappe.new_doc("Stock Entry")
		se.update({ "purpose": "Material Issue" , 
			"stock_entry_type": "Material Issue" , 
			"posting_date" : doc.raised_date })
		for se_item in doc.items:
			se.append("items", { 
				"item_code":se_item.item_code, 
				"item_group": se_item.item_group, 
				"item_name":se_item.item_name, 
				"amount":se_item.amount, 
				"qty": se_item.qty, 
				"uom":se_item.uom,
				"conversion_factor": se_item.conversion_factor }) 
		
		frappe.msgprint('Stock Entry is created please submit the stock entry')
		se.insert()
		se.save()


	
@frappe.whitelist()
def get_stock_balance_for(item_code):
	print("\n\n\n entering - ")	
	item_stock_qty = frappe.db.sql("""select ifnull(actual_qty,0) as actual_qty from `tabBin` where item_code = %s order by creation Desc limit 1""",(item_code),as_dict=1)
	print("\n\n\n taking value - ")
	print(item_stock_qty[0].actual_qty)
	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0
