
import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_user_permission(doc, method):
    """
    Synchronize User Permissions based on the 'Users Role' assigned to the User.
    This version is ADDITIVE-ONLY: it will add missing permissions but NEVER delete existing ones.
    """
    if not doc.custom_user_role:
        return

    try:
        user_role = frappe.get_doc("Users Role", doc.custom_user_role)
    except frappe.DoesNotExistError:
        return

    # 1. Get current permissions for this user to avoid duplicates
    existing_perms = frappe.get_all("User Permission", 
        filters={"user": doc.name}, 
        fields=["allow", "for_value"]
    )
    current_perm_set = {(p.allow, p.for_value) for p in existing_perms}

    # 2. Add missing permissions from User Role
    added_count = 0
    for detail in user_role.users_role_details:
        if not detail.allow or not detail.for_value:
            continue
            
        perm_key = (detail.allow, detail.for_value)
        
        if perm_key not in current_perm_set:
            try:
                # Add the permission
                from frappe.permissions import add_user_permission
                add_user_permission(
                    doctype=detail.allow,
                    name=detail.for_value,
                    user=doc.name,
                    is_default=detail.is_default,
                    applicable_for=detail.applicable_for if not detail.apply_to_all_document_types else None,
                    hide_descendants=detail.hide_descendants
                )
                added_count += 1
                current_perm_set.add(perm_key)
            except Exception as e:
                frappe.log_error(f"Error adding permission in Super Admin: {str(e)}", "Permission Sync")

    if added_count > 0:
        frappe.msgprint(f"Synced {added_count} new permissions for {doc.name}", alert=True)

    return
