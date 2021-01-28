
frappe.ui.form.on("Task", {
	setup: function (frm) {
        frm.set_query('serial_no_cf', () => {
            return {
                filters: {
                    "item_code": frm.doc.item_cf
                }
            }
        })
    }
})