
               
import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_user_permission(doc, method):
    user = frappe.get_doc("User", doc.name)
    
    # Skip if no custom user role is assigned
    if not user.custom_user_role:
        return

    user_role = frappe.get_doc("Users Role", user.custom_user_role)

    # Create a set of current permissions from the role
    current_permissions = {
        (role_detail.allow, role_detail.for_value)
        for role_detail in user_role.users_role_details
    }

    # Get existing user permissions for this user
    existing_permissions = frappe.get_all(
        "User Permission",
        filters={"user": user.name},
        fields=["name", "allow", "for_value"]
    )

    # Remove permissions that no longer exist in the role
    for permission in existing_permissions:
        permission_tuple = (permission["allow"], permission["for_value"])
        if permission_tuple not in current_permissions:
            frappe.delete_doc("User Permission", permission["name"], ignore_permissions=True)

    # Add new permissions based on role details
    for role_detail in user_role.users_role_details:
        permission_exists = frappe.get_all(
            "User Permission",
            filters={
                "user": user.name,
                "allow": role_detail.allow,
                "for_value": role_detail.for_value
            }
        )

        # Skip if permission already exists
        if not permission_exists:
            user_permission = frappe.new_doc("User Permission")
            user_permission.user = user.name
            user_permission.allow = role_detail.allow

            # Handle specific logic for 'Employee' and 'User' doctypes
            if role_detail.allow == "Employee":
                linked_employee = frappe.db.get_value("Employee", {"user_id": user.name}, "name")
                if linked_employee:
                    user_permission.for_value = linked_employee
                else:
                    frappe.log_error(f"Employee record not found for user: {user.name}", "Missing Employee")
                    continue  # Skip adding this permission

            elif role_detail.allow == "User":
                linked_user = frappe.db.get_value("User", {"name": user.name})
                if linked_user:
                    user_permission.for_value = linked_user
                else:
                    frappe.log_error(f"User record not found for user: {user.name}", "Missing User")
                    continue  # Skip adding this permission

            else:
                user_permission.for_value = role_detail.for_value or ""  

            # Set additional fields
            user_permission.applicable_for = role_detail.applicable_for
            user_permission.is_default = role_detail.is_default
            user_permission.apply_to_all_doctypes = role_detail.apply_to_all_document_types
            user_permission.hide_descendants = role_detail.hide_descendants

            # Save the permission
            user_permission.save(ignore_permissions=True)

    frappe.db.commit()
