import frappe
from  frappe import _
from frappe.installer import update_site_config,_update_config_file
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from super_admin.super_admin.custom_field.custom_field import CREATE_FIELDS

def execute():
    create_custom_fields(CREATE_FIELDS, ignore_validate=True)
   
