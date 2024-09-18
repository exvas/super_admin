import frappe
from frappe.model.document import Document


@frappe.whitelist()
def create_user_permission(doc, method):
    user = frappe.get_doc("User", doc.name)
    if not user.custom_user_role:
        return

    user_role = frappe.get_doc("Users Role", user.custom_user_role)

    current_permissions = {
        (role_detail.allow, role_detail.for_value)
        for role_detail in user_role.users_role_details
    }

    existing_permissions = frappe.get_all(
        "User Permission",
        filters={"user": user.name},
        fields=["name", "allow", "for_value"]
    )

    for permission in existing_permissions:
        permission_tuple = (permission["allow"], permission["for_value"])
        if permission_tuple not in current_permissions:
            frappe.delete_doc("User Permission", permission["name"], ignore_permissions=True)


    for role_detail in user_role.users_role_details:
        permission_exists = frappe.get_all(
            "User Permission",
            filters={
                "user": user.name,
                "allow": role_detail.allow,
                "for_value": role_detail.for_value
            }
        )

        if not permission_exists:
            user_permission = frappe.new_doc("User Permission")
            user_permission.user = user.name
            user_permission.allow = role_detail.allow

            if role_detail.allow == "Employee":
                linked_employee = frappe.db.get_value("Employee", {"user_id": user.name}, "name")
                user_permission.for_value = linked_employee if linked_employee else role_detail.for_value
            else:
                user_permission.for_value = role_detail.for_value
            if role_detail.allow == "User":
                linked_user = frappe.db.get_value("User", {"name": user.name})
                user_permission.for_value = linked_user if linked_user else role_detail.for_value




            user_permission.applicable_for = role_detail.applicable_for
            user_permission.is_default = role_detail.is_default
            user_permission.apply_to_all_doctypes = role_detail.apply_to_all_document_types
            user_permission.hide_descendants = role_detail.hide_descendants

            user_permission.insert(ignore_permissions=True)

    frappe.db.commit()

               
