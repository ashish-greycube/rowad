import  frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint,flt,add_years,nowdate,add_days
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.contacts.doctype.address.address import get_company_address


def validate_sales_order_item_user_allocation(self,method):
    # creat a compact dictionary ex. {"Item1:1","Item2:2"}
    so_items={}
    for item in self.get("items"):
        if item.item_code in so_items:
            qty=so_items.get(item.item_code)
            qty=qty+item.qty
            so_items.update({item.item_code:qty})
        else:
            so_items.update({item.item_code:item.qty})

    user_items={}
    for item in self.get("sales_order_item_user_allocation"):
        if item.item in user_items:
            qty=user_items.get(item.item)
            qty=qty+item.qty
            user_items.update({item.item:qty})
        else:
            user_items.update({item.item:item.qty})



    # check for missing key in user allocation table
    for key in so_items.keys():
        if not key in user_items:
            frappe.throw(
                _('<b>{0}</b> item is missing from user allocation table.').format(key), 
                title=_('Missing item error')
                )

    # check for qty , assuming all key matches
    for key in so_items.keys() & user_items.keys():
        if user_items[key]!=so_items[key]:
            frappe.throw(
                _("For <b>{0}</b> item, qty in sales order is <b>{1}</b> whereas in user allocation it is <b>{2}</b>.<br>Please correct the quantity.").format(key,so_items[key],user_items[key]),
                title=_('Qantity mismatch error')
                )

@frappe.whitelist()
def make_task_based_project(source_name, target_doc=None):
    so=frappe.get_doc('Sales Order',source_name)

    doclist=[]
    def postprocess(source, doc):
        doc.project_type = "External"
        doc.project_name = source.name

    doc = get_mapped_doc("Sales Order", source_name, {
        "Sales Order": {
            "doctype": "Project",
            "validation": {
                "docstatus": ["=", 1]
            },
            "field_map":{
                "name" : "sales_order",
                "base_grand_total" : "estimated_costing",
            }
        },
    }, target_doc, postprocess)
    doc.save(ignore_permissions=True)
    doclist.append(doc)
    if doc:
        for item in so.get("sales_order_item_user_allocation"):
            for qty in range(cint(item.qty)):
                task=frappe.new_doc("Task")
                task.project=doc.name
                task.subject=item.item
                task.item_cf=item.item
                task.completed_by=item.user
                task.save(ignore_permissions=True)
                doclist.append(task)
    return doclist

def validate_task_and_create_delivery_note_maintenance_schedule(self,method):
    doclist=[]
    if self.status=='Completed' and self.project.startswith('SAL-ORD-'):
        serial_nos=frappe.db.get_list('Serial No', filters={'item_code': ['=', self.item_cf],'status': ['=', 'Active']})
        valid_serial_nos= [s['name'] for s in serial_nos]

        if len(serial_nos)>0 and not self.serial_no_cf:
            frappe.throw(
                _('Please specify serial no. It could be one of {0}').format(valid_serial_nos),
                title=_('Missing Serial No.'))
        elif len(serial_nos)>0 and (self.serial_no_cf not in valid_serial_nos):
            frappe.throw(
                _('Please specify correct serial no. It could be one of {0}').format(valid_serial_nos),
                title=_('Incorrect Serial No.'))  
    # create delivery note
        delivery_note = make_delivery_note(source_name=self.project,task_name=self.item_cf,serial_no=self.serial_no_cf)
        doclist.append(delivery_note)
        frappe.msgprint(_("Delivery Note {0} created").format("<a href='#Form/Delivery Note/{0}'>{0}</a>".format(delivery_note.name)))        



def make_delivery_note(source_name,task_name,serial_no=None,target_doc=None, skip_item_mapping=False):
    def set_missing_values(source, target):
        target.ignore_pricing_rule = 1
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        if source.company_address:
            target.update({'company_address': source.company_address})
        else:
            # set company address
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Delivery Note", 'company_address', target.company_address))

    def update_item(source, target, source_parent):
        target.base_amount = flt(source.base_rate)
        target.amount = flt(source.rate)
        target.is_maintenance_applicable_cf=source.is_maintenance_applicable_cf
        target.maintenance_for_years_cf=source.maintenance_for_years_cf
        target.qty = 1
        serial_no_warehouse=None
        if serial_no:
            target.serial_no=serial_no
            serial_no_warehouse= frappe.db.get_value('Serial No', serial_no, 'warehouse') 
        target.warehouse = serial_no_warehouse or source.warehouse or None
        item = get_item_defaults(target.item_code, source_parent.company)
        item_group = get_item_group_defaults(target.item_code, source_parent.company)

        if item:
            target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
                or item.get("buying_cost_center") \
                or item_group.get("buying_cost_center")

    mapper = {
        "Sales Order": {
            "doctype": "Delivery Note",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Sales Taxes and Charges": {
            "doctype": "Sales Taxes and Charges",
            "add_if_empty": True
        },
        "Sales Team": {
            "doctype": "Sales Team",
            "add_if_empty": True
        }
    }

    if not skip_item_mapping:
        mapper["Sales Order Item"] = {
            "doctype": "Delivery Note Item",
            "field_map": {
                "rate": "rate",
                "name": "so_detail",
                "parent": "against_sales_order",
            },
            "postprocess": update_item,
            "condition": lambda doc: abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier!=1 and doc.item_code == task_name
        }

    target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)
    [target_doc.items.remove(d) for d in target_doc.get('items') if d.idx > 1]
    target_doc.save(ignore_permissions=True)
    return target_doc                

@frappe.whitelist()
def make_maintenance_schedule(source_name, target_doc=None):
    doclist=[]
    STANDARD_USERS = ("Guest", "Administrator")
    sales_person_name=None
    user = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
    if user:
        employee=frappe.db.get_list('Employee', filters={'user_id': ['=', user]},fields=['name'])
        if len(employee)>0:
            sales_person = frappe.db.get_list('Sales Person', filters={'employee': ['=', employee[0].name]},fields=['name'])
            if len(sales_person)>0:
                sales_person_name=sales_person[0].name   
    def set_missing_values(source, target):
        target.project_cf=source.project
         # + 1 
        target.transaction_date=add_days(source.posting_date,1)
        target.run_method("set_missing_values")
        target.run_method("generate_schedule")

    def update_item(source, target, source_parent):
        if source.is_maintenance_applicable_cf==0:
            frappe.msgprint(_('Delivery Note item <b>{0}</b> has no value for <i>Is Maintenance Applicable ?</i>').format(source.item_code),
            title='Maintenance Schedule cannot be created.')
            return False
        elif source.is_maintenance_applicable_cf==1:
            if source.maintenance_for_years_cf<2:
                frappe.msgprint(_('Delivery Note item <b>{0}</b> has <i>Maintenance For Years</i> values as <b>{1}</b>. <br> It should be greater than 1.').format(source.item_code,source.maintenance_for_years_cf),
                title='Incorrect Maintenance For Years values.')
                return False 
        # + 1                       
        target.start_date = add_days(source_parent.posting_date,1)
        target.end_date = add_years(target.start_date, source.maintenance_for_years_cf)
        target.periodicity = 'Yearly'
        target.no_of_visits=source.maintenance_for_years_cf
        target.serial_no=source.serial_no
        target.sales_person= sales_person_name or 'Sales Team'
    # maint_schedule = frappe.db.sql("""select t1.name
    # 	from `tabMaintenance Schedule` t1, `tabMaintenance Schedule Item` t2
    # 	where t2.parent=t1.name and t2.maintenance_schedule=%s and t1.docstatus=1""", source_name)

    # if not maint_schedule:
    target_doc = get_mapped_doc("Delivery Note", source_name, {
        "Delivery Note": {
            "doctype": "Maintenance Schedule",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Delivery Note Item": {
            "doctype": "Maintenance Schedule Item",
            "field_map": {
                "parent": "maintenance_schedule"
            },
            "postprocess": update_item,
            "add_if_empty": True
        }
    }, target_doc,set_missing_values)
    target_doc.save(ignore_permissions=True)
    doclist.append(target_doc)
    return doclist    


@frappe.whitelist()
def make_maintenance_visit(source_name, target_doc=None):
    doclist=[]
    items=[]
    STANDARD_USERS = ("Guest", "Administrator")
    sales_person_name=None
    user = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
    if user:
        employee=frappe.db.get_list('Employee', filters={'user_id': ['=', user]},fields=['name'])
        if len(employee)>0:
            sales_person = frappe.db.get_list('Sales Person', filters={'employee': ['=', employee[0].name]},fields=['name'])
            if len(sales_person)>0:
                sales_person_name=sales_person[0].name
    
    def update_status(source, target, parent):
        target.project_cf=source.project_cf
        target.maintenance_type = "Scheduled"

    def update_item(source, target, source_parent):
        items.append({'item_code':source.item_code,'qty':1,'stock_uom':frappe.db.get_value('Item', source.item_code, 'stock_uom')})
        if sales_person_name:
            target.service_person=sales_person_name
        else:
            target.service_person='Sales Team'

    doc = get_mapped_doc("Maintenance Schedule", source_name, {
        "Maintenance Schedule": {
            "doctype": "Maintenance Visit",
            "field_map": {
                "name": "maintenance_schedule"
            },
            "validation": {
                "docstatus": ["=", 1]
            },
            "postprocess": update_status
        },
        "Maintenance Schedule Item": {
            "doctype": "Maintenance Visit Purpose",
            "field_map": {
                "parent": "prevdoc_docname",
                "parenttype": "prevdoc_doctype"
            },
            "postprocess": update_item,
        }    
    }, target_doc)
    # for item in items:
    #     row=doclist.append('maintenance_consumed_items_cf',item)
    # doc.save(ignore_permissions=True)
    # doclist.append(doc)
    return doc    

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
    doclist=[]
    def update_item(source, target, source_parent):
        sales_person = source_parent.get('purposes')[0].service_person
        s_warehouse=frappe.db.get_value('Sales Person', sales_person, 'default_warehouse_cf')
        target.s_warehouse = s_warehouse
        if source_parent.project_cf:
            target.cost_center = frappe.db.get_value('Project', source_parent.project_cf, 'cost_center') or None

    def set_missing_values(source, target):
        target.stock_entry_type = "Material Issue"
        target.calculate_rate_and_amount()
        target.set_missing_values()
        target.set_stock_entry_type()

    doc = get_mapped_doc("Maintenance Visit", source_name, {
        "Maintenance Visit": {
            "doctype": "Stock Entry",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Maintenance Consumed Items": {
            "doctype": "Stock Entry Detail",
            "field_map": {
                "item_code":"item_code",
                "qty":"qty",
                "stock_uom":"stock_uom"
            },
            "postprocess": update_item
        }
    }, target_doc, set_missing_values)
    doc.save(ignore_permissions=True)
    doclist.append(doc)
    return doclist   
