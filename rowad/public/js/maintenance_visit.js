frappe.ui.form.on('Maintenance Visit', {
    setup:function(frm) {
        frm.set_query('item_code', 'maintenance_consumed_items_cf', () => {
            return {
                filters: {
                    has_serial_no: 0,
                    is_stock_item:1
                }
            }
        })    
    },  
    on_submit:function(frm) {
        make_stock_entry(frm)
    },
	refresh: function(frm) {
    }
})
function make_stock_entry(frm) {
    frappe.model.open_mapped_doc({
        method: "rowad.api.make_stock_entry",
        source_name: frm.doc.name,
        frm: frm
    }); 
}

function make_stock_entry(frm) {
    frappe.call({
        method: "rowad.api.make_stock_entry",
        args: {
            "source_name": cur_frm.doc.name
        },
        freeze: true,
        callback: function (r) {
            if (r.message) {
                let url_list = ''
                r.message.forEach(function (doc, i) {
                        url_list += '<a href="#Form/Stock Entry/' + doc.name + '" target="_blank">' + doc.name + '</a><br>'
                        window.open("#Form/Stock Entry/" + doc.name)                   
                });
                setTimeout(urlpopup, 1000);
                function urlpopup() {
                    frappe.msgprint({
                        title: __('Following Stock Entry is created'),
                        indicator: 'green',
                        message: __(url_list)
                    })
                }
            }
        }
    });    
}