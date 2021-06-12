from __future__ import unicode_literals
from frappe import _
import frappe
def get_data():
	return [
		{
			"label": _("Key Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Receipt Status",
					"doctype": "Stock Entry",
				},		
			]
		}
    ]    