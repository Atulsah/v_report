from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Key Report"),
			"icon": "icon-cog",
			"items": [	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order Status",
					"doctype": "Sales Order"
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Status",
					"doctype": "Purchase Order"
				},							
			]
		}
	]
