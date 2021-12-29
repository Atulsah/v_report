// Copyright (c) 2016, Frappe and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Preventive Maintenance"] = {
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
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd":1
		}
	]
};
