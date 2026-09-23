import frappe


@frappe.whitelist()
def share_delivery_order(delivery_order_name, user_email):
    frappe.share.add(
        "Delivery Order",
        delivery_order_name,
        user_email,
        read=1
    )

def delivery_order_query_conditions(user):
    if not user:
        user = frappe.session.user

    if "DP Rider" in frappe.get_roles(user):
        return """
            `tabDelivery Order`.`assigned_rider` IN (
                SELECT `name`
                FROM `tabRider`
                WHERE `user` = {user}
            )
        """.format(
            user=frappe.db.escape(user)
        )

    return ""


@frappe.whitelist()
def get_delivery_orders_unsafe():
    return frappe.get_all(
        "Delivery Order",
        fields=["*"]
    )


@frappe.whitelist()
def get_delivery_orders_safe():
    orders = frappe.get_list(
        "Delivery Order",
        fields=["*"]
    )

    if "DP Ops Manager" not in frappe.get_roles():
        for order in orders:
            order.pop("customer_phone", None)
            order.pop("customer_email", None)

    return orders


import frappe
from frappe.utils import now


@frappe.whitelist()
def record_delivery_attempt(delivery_order_name, outcome, failure_reason=None):
	
	delivery_order = frappe.get_doc(
		"Delivery Order",
		delivery_order_name
	)

	max_attempts = frappe.db.get_single_value(
		"Dispatch Settings",
		"max_delivery_attempts"
	) or 0


	if outcome == "Failed":

		delivery_order.delivery_attempts_count = (delivery_order.delivery_attempts_count or 0) + 1

		if failure_reason:
			delivery_order.failure_reason = failure_reason

		if delivery_order.delivery_attempts_count < max_attempts:

			delivery_order.status = "Re-attempt Scheduled"

		else:

			delivery_order.status = "Escalated"

	
	elif outcome == "Delivered":

		delivery_order.status = "Delivered"

		delivery_order.delivered_on = now()

	
	else:
		frappe.throw("Outcome must be either 'Failed' or 'Delivered'.")

	delivery_order.save(ignore_permissions=True)

	frappe.publish_realtime(
		"delivery_status_changed",
		{
			"delivery_order": delivery_order.name,
			"status": delivery_order.status,
			"user": delivery_order.owner
		}
	)

	return {
		"status": delivery_order.status,
		"delivery_attempts_count": delivery_order.delivery_attempts_count
	}


@frappe.whitelist()
def rename_rider(old, new):
    return frappe.rename_doc(
        "Rider",
        old,
        new,
        merge=False
    )