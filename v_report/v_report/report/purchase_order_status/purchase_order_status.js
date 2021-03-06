// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Status"] = {
	"filters": [
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd":1
         },

		 {
            "fieldname":"item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "reqd":0
         },

		{
		    "fieldname":"from_date",
		    "label": __("Purchase Date From"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_start_date"),
		    "reqd":1
		},

		{
		    "fieldname":"to_date",
		    "label": __("Purchase Date To"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_end_date"),
		    "reqd":1
		}

	]
};

