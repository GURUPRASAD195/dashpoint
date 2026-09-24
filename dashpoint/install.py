import frappe


def after_install():
    create_default_delivery_zones()
    create_default_dispatch_settings()

    frappe.msgprint(
        "DashPoint installation completed successfully."
    )


def create_default_delivery_zones():
    zones = [
        "North Zone",
        "South Zone",
        "Central Zone"
    ]

    for zone in zones:
        if not frappe.db.exists("Delivery Zone", zone):
            frappe.get_doc({
                "doctype": "Delivery Zone",
                "zone_name": zone
            }).insert(ignore_permissions=True)


def create_default_dispatch_settings():
    if not frappe.db.exists("Dispatch Settings", "Dispatch Settings"):
        frappe.get_doc({"doctype": "Dispatch Settings"}).insert(ignore_permissions=True)