from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Container"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Container Planning",
					"onboard": 1,
					"dependencies": [],
					"description": _("Container Planning"),
				},	
			]
		},
		{
			"label": _("Equipment"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Register",
					"onboard": 1,
					"dependencies": [],
					"description": _("Equipment Register"),
				},
                {
					"type": "doctype",
					"name": "Daily Preventive Maintenance",
					"onboard": 1,
					"dependencies": [],
					"description": _("Daily Preventive Maintenance"),
				},	
                {
					"type": "doctype",
					"name": "Raised Equipment Issue",
					"onboard": 1,
					"dependencies": [],
					"description": _("Raised Equipment Issue"),
				}	
			]
		},
		{
			"label": _("Key Report"),
			"icon": "icon-cog",
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
					"name": "Material Receipt Status",
					"doctype": "Stock Entry",
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Status",
					"doctype": "Purchase Order",
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order Status Report",
					"doctype": "Sales Order",
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Status Report",
					"doctype": "Sales Order",
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Ordered Item To Be Manufacture",
					"doctype": "Sales Order",
				},		
			]
		}
    ]    