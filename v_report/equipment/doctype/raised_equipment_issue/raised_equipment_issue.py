# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RaisedEquipmentIssue(Document):
	
	def on_submit(self):
		self.create_stock_entry()


	def create_stock_entry(doc):
		if doc.items :
			se = frappe.new_doc("Stock Entry")
			se.update({ "purpose": "Material Issue",
				"company" : doc.company,
				"posting_date": doc.expected_resolve_date, 
				"stock_entry_type": "Material Issue" })
			for se_item in doc.items:
				se.append("items", { 
					"s_warehouse": se_item.warehouse,
					"item_code":se_item.item_code,  
					"item_name":se_item.item_name, 
					"amount":1, 
					"qty": se_item.quantity , 
					"uom":se_item.uom }) 
			frappe.msgprint('Stock Entry is created please submit the stock entry')
			se.insert()
			se.save()



