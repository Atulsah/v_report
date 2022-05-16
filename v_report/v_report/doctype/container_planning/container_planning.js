// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Planning', {
	// refresh: function(frm) {
	//	description: function(frm, cdt, cdn) {
	//		var cur_doc = locals[cdt][cdn];
	//		cur_doc.reference_type = frm.doctype;
	//		cur_doc.reference_name = frm.doc.container_number;
	//		frm.refresh_fields();

	// }

});

frappe.ui.form.on('Container Planning Item', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name for e.g bbfcb8da6a
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
    }
})

