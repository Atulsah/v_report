# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DailyPreventiveMaintenance(Document):
	

	def on_submit(self):
		self.raise_equipment_issue()


	def raise_equipment_issue(doc):
		for se_item in doc.equipments:
			se = frappe.new_doc("Raised Equipment Issue")
			se.update({ 
				"company" : doc.company, 
				"daily_preventive_maintenance_id" : doc.name,
				"raised_date" : doc.date,
				"maintenance_equipment_list_id" :se_item.name, 
				"equipment_name": se_item.equipment_name, 
				"issue_raised" : se_item.abnormalities,
				"remark" : se_item.remark
				}) 
			se.insert()
			se.save()

	