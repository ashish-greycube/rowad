frappe.ui.form.on("Sales Order", {
    on_submit:function(frm) {
        make_task_based_project(frm)
    },    
    refresh:function(frm){
        if (frm.doc.docstatus==1) {     
        if(frm.doc.status !== 'Closed') {
            if(frm.doc.status !== 'On Hold') {
                    // project
					if(flt(frm.doc.per_delivered, 2) < 100) {
                        frm.add_custom_button(__('Task based Project'), () => make_task_based_project(frm), __('Create'));
                }                
            }
        }  
    }      
    },
	setup: function(frm) {
        frm.fields_dict.sales_order_item_user_allocation.grid.get_field('item').get_query =
        function() {
            return {
                filters: {
                    "item_code": ["in", frm.doc.items.map(function(value){return(value.item_code)})]
                }
            }
        }
    }
})
frappe.ui.form.on("Sales Order Item", {
	item_code: function(frm,cdt,cdn) {
        var row = locals[cdt][cdn];
        frappe.db.get_value('Item', row.item_code, 'is_maintenance_applicable_cf')
        .then(r => {
            if (r.message.is_maintenance_applicable_cf==1) {
    			row.is_maintenance_applicable_cf = 1;
			    refresh_field("is_maintenance_applicable_cf", cdn, "items");            
            }
        })}        

})
function make_task_based_project(frm) {
    frappe.call({
        method: "rowad.api.make_task_based_project",
        args: {
            "source_name": cur_frm.doc.name
        },
        freeze: true,
        callback: function (r) {
            if (r.message) {
                let url_list = ''
                r.message.forEach(function (doc, i) {
                    if (i==0) 
                    {
                        url_list += '<a href="#Form/Project/' + doc.name + '" target="_blank">' + doc.name + '</a><br>'
                        window.open("#Form/Project/" + doc.name)                      
                    }
                    else{
                        url_list += '<a href="#Form/Task/' + doc.name + '" target="_blank">' + doc.name + '</a><br>'
                        window.open("#Form/Task/" + doc.name)                   
                    }
                });
                setTimeout(urlpopup, 1000);
                function urlpopup() {
                    frappe.msgprint({
                        title: __('Following Project & Tasks are created'),
                        indicator: 'green',
                        message: __(url_list)
                    })
                }
            }
        }
    });    
}