import frappe

def get_dispatch_center_name():
    return frappe.db.get_single_value(
        "Dispatch Settings",
        "dispatch_center_name"
    )