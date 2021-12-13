// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Status Report"] = {
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
            "fieldname":"foreign_buyer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd":1
         },
		 {
		    "fieldname":"report_type",
		    "label": __("Report Type"),
			"fieldtype": "Select",
			"options": ["Ordered-Item-Report","Dispatched-Item-Report","Mixed-Report"],
			"default": "Ordered-Item-Report",
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
		}

	]

};
