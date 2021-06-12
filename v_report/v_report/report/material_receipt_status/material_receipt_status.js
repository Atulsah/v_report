// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Material Receipt Status"] = {
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
		    "fieldname":"from_date",
		    "label": __("Sold Date From"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_start_date"),
		    "reqd":1
		},

		{
		    "fieldname":"to_date",
		    "label": __("Sold Date To"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_end_date"),
		    "reqd":1
		},

        {
            "fieldname":"warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd":0
         },

		 {
            "fieldname":"item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd":0
         }

		
	]
};
