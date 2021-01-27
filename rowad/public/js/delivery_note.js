frappe.ui.form.on("Delivery Note", {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1 ) {
            frm.add_custom_button(__('Maintenance Schedule'), () => make_maintenance_schedule(frm), __('Create'));            
		}
	}
});  

function make_maintenance_schedule(frm) {
    frappe.call({
        method: "rowad.api.make_maintenance_schedule",
        args: {
            "source_name": cur_frm.doc.name
        },
        freeze: true,
        callback: function (r) {
            if (r.message) {
                let url_list = ''
                r.message.forEach(function (doc, i) {
                        url_list += '<a href="#Form/Maintenance Schedule/' + doc.name + '" target="_blank">' + doc.name + '</a><br>'
                        window.open("#Form/Maintenance Schedule/" + doc.name)                   
                });
                setTimeout(urlpopup, 1000);
                function urlpopup() {
                    frappe.msgprint({
                        title: __('Following Maintenance Schedule is created'),
                        indicator: 'green',
                        message: __(url_list)
                    })
                }
            }
        }
    });    
}