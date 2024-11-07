import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from super_admin.super_admin.custom_field.custom_field import CREATE_FIELDS

def after_install():
    create_custom_fields(CREATE_FIELDS, ignore_validate=True)


def after_migrate():
    print("Custom Field")
    create_custom_fields(CREATE_FIELDS, ignore_validate=True)

def before_uninstall():
    
    print('delete custom field')
    delete_custom_fields(CREATE_FIELDS)

def delete_custom_fields(custom_fields):
    for doctypes, fields in custom_fields.items():
        if isinstance(fields, dict):
            # only one field
            fields = [fields]

        if isinstance(doctypes, str):
            # only one doctype
            doctypes = (doctypes,)

        for doctype in doctypes:
            frappe.db.delete(
                "Custom Field",
                {
                    "fieldname": ("in", [field["fieldname"] for field in fields]),
                    "dt": doctype,
                },
            )

            frappe.clear_cache(doctype=doctype)
