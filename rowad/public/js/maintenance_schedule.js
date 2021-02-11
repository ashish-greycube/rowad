frappe.ui.form.on('Maintenance Schedule', {
	refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Rowad Maintenance Visit'), function() {
				frappe.model.open_mapped_doc({
					method: "rowad.api.make_maintenance_visit",
					source_name: frm.doc.name,
					frm: frm
				});
			}, __('Create'));
		}
    }
})