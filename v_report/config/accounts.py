from __future__ import unicode_literals
from frappe import _
import frappe
def get_data():
	return [
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order Status",
					"doctype": "Sales Order",
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Ordered Item To Be Manufacture",
					"doctype": "Sales Order",
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Status",
					"doctype": "Purchase Order",
				},			
			]
		}
    ]    