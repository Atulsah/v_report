// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Raised Equipment Issue', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on("Raised Equipment Issue", "validate", function(frm){ 
	set_current_stock(frm);	
});

frappe.ui.form.on("Used Item List", "current_stock", function(frm, cdt, cdn){ 
	set_current_stock(frm);
});



frappe.ui.form.on("Raised Equipment Issue", {
	// Fetch item quantity on select item 
	set_current_stock_qty: function(frm, cdt, cdn) {
	  var d = frappe.model.get_doc(cdt, cdn);
	  if(d.item_code) {
		frappe.call({
		  method: "v_report.equipment.doctype.raised_equipment_issue.raised_equipment_issue.get_stock_balance_for",
		  args: {
			item_code: d.item_code
		  },
		  
		  callback: function(r) {
			frappe.model.set_value(cdt, cdn, "current_stock", r.message.current_stock);
		  }
		});
	  }
	}
  });

  frappe.ui.form.on("Used Item List","current_stock", function(frm, cdt, cdn) {
	frm.events.set_current_stock_qty(frm, cdt, cdn);
	frm.set_value("from_warehouse", frm.doc.source_warehouse);
  }	
);