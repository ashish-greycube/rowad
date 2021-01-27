frappe.ui.form.on("Item", {
    is_maintenance_applicable_cf:function(frm) {
        if (frm.doc.is_maintenance_applicable_cf === 1 ) {
            if (frm.doc.maintenance_for_years_cf==0) {
                frm.set_value('maintenance_for_years_cf', '')
            }
        } else {
            frm.set_value('maintenance_for_years_cf', 0)
        }
        cur_frm.toggle_reqd('maintenance_for_years_cf', (cur_frm.doc.is_maintenance_applicable_cf === 1 ));
    },
	refresh: function(frm) {
        cur_frm.toggle_reqd('maintenance_for_years_cf', (cur_frm.doc.is_maintenance_applicable_cf === 1 ));
	}
}); 