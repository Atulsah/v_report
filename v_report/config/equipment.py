from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Doctype"),
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
				},	
			]
		}
    ]    