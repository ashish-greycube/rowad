
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def after_migrate():
    custom_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Task",
            "label": "Delivery Note",
            "fieldname": "delivery_note_cf",
            "fieldtype": "Link",
            "options": "Delivery Note",
            "translatable": 0,
            "insert_after": "parent_task"
        }, 
        {
            "doctype": "Custom Field",
            "dt": "Task",
            "label": "Shipping Address",
            "fieldname": "shipping_address_name_cf",
            "fieldtype": "Link",
            "options": "Address",
            "translatable": 0,
            "read_only":1,
            "fetch_from":"delivery_note_cf.shipping_address_name",
            "insert_after": "delivery_note_cf"
        },
        {
            "doctype": "Custom Field",
            "dt": "Maintenance Schedule",
            "label": "Shipping Address",
            "fieldname": "shipping_address_name_cf",
            "fieldtype": "Link",
            "options": "Address",
            "translatable": 0,
            "read_only":1,
            "insert_after": "transaction_date"
        } ,
        {
            "doctype": "Custom Field",
            "dt": "Maintenance Visit",
            "label": "Shipping Address",
            "fieldname": "shipping_address_name_cf",
            "fieldtype": "Link",
            "options": "Address",
            "translatable": 0,
            "read_only":1,
            "insert_after": "contact_email"
        }                 
    ]
    for d in custom_fields:
        if not frappe.get_meta(d["dt"]).has_field(d["fieldname"]):
            frappe.get_doc(d).insert()
