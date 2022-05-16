# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values

class ContainerPlanning(Document):
	pass

def validate(self):
	update_item(self)

@frappe.whitelist()
def make_planning(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)
	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		doc = frappe.get_doc(target)

	def update_item(source, target, source_parent):
		target.s_o_no = source_parent.name
	
	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Container Planning",
			"field_map": {
				"Sales Order No": "name"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Container Planning Item",
			"field_map": {
			},
			"postprocess": update_item
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist



@frappe.whitelist(methods=['POST', 'PUT'])
def submit(doc):
	'''Submit a document
	:param doc: JSON or dict object to be submitted remotely'''
	if isinstance(doc, str):
		doc = json.loads(doc)

	doc = frappe.get_doc(doc)
	doc.submit()

	return doc.as_dict()

@frappe.whitelist(methods=['POST', 'PUT'])
def cancel(doctype, name):
	'''Cancel a document
	:param doctype: DocType of the document to be cancelled
	:param name: name of the document to be cancelled'''
	wrapper = frappe.get_doc(doctype, name)
	wrapper.cancel()

	return wrapper.as_dict()

@frappe.whitelist(methods=['DELETE', 'POST'])
def delete(doctype, name):
	'''Delete a remote document
	:param doctype: DocType of the document to be deleted
	:param name: name of the document to be deleted'''
	frappe.delete_doc(doctype, name, ignore_missing=False)

#@frappe.whitelist(methods=['POST', 'PUT'])
def update_items(doc,method):
	frappe.errprint("calculate works")
	from frappe.utils import flt
	for item in doc.get("items"):
		if item.planned_qty == 0 or "":
			item.planned_qty= flt(item.qty)
			item.difference_qty = 0
		else:
			item.difference_qty = flt(item.planned_qty - item.qty)

	doc.custom_field = "value"
	return doc


def create_stock_entry(doc, handler=""):
    se = frappe.new_doc("Stock Entry")
    se.update({ "purpose": "Material Transfer" , "stock_entry_type": "Material Transfer" , "from_warehouse": "Reservation Warehouse - G" , "to_warehouse": "Finished Goods - G" })
    for se_item in doc.items:
        se.append("items", { "item_code":se_item.item_code, "item_group": se_item.item_group, "item_name":se_item.item_name, "amount":se_item.amount, "qty": se_item.qty , "uom":se_item.uom, "conversion_factor": se_item.conversion_factor }) 
    frappe.msgprint('Stock Entry is created please submit the stock entry')
    se.insert()