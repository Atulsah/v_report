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
            "fieldname":"warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
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

	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "flag" && data && data.flag == 0) {
			value = "<span style='color:red;background-color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "flag" && data && data.flag == 1) {
			value = "<span style='color:green;background-color:green'>" + value + "</span>";
		}

		return value;
	}


};