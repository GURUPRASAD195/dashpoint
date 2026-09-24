
import frappe
from frappe.model.document import Document


class DeliveryOrder(Document):

	def validate(self):
		if (not self.customer_phone or not self.customer_phone.isdigit() 
	  	or len(self.customer_phone) != 10):
			frappe.throw("Customer phone must be exactly 10 digits.")

		statuses_requiring_rider = ["In Transit", "Delivered", "Delivery Failed", "Re-attempt Scheduled", "Escalated"]

		if (self.status in statuses_requiring_rider and not self.assigned_rider):
			frappe.throw("Assigned Rider is mandatory for this status.")

		if (self.status == "Delivery Failed" and not self.failure_reason):
			frappe.throw("Failure Reason is mandatory when delivery has failed.")

		packaging_total = 0

		for row in self.packaging_used:

			row.total_price = ((row.quantity or 0) * (row.unit_price or 0))

			packaging_total += row.total_price

		self.packaging_total = packaging_total

		if not self.delivery_fee:

			self.delivery_fee = frappe.db.get_single_value("Dispatch Settings", "default_delivery_fee") or 0

		self.final_amount = ((self.packaging_total or 0) + (self.delivery_fee or 0))


	def before_submit(self):
		if self.status != "Delivered":
			return

		for row in self.packaging_used:

			stock_qty = frappe.db.get_value("Packaging Material", row.material, "stock_qty")

			if stock_qty is None:
				frappe.throw(f"Packaging Material {row.material} was not found.")

			
			if stock_qty < row.quantity:
				frappe.throw(f"Insufficient stock for {row.material}. Available: {stock_qty}, Required: {row.quantity}")


	def on_submit(self):
		if self.status != "Delivered":
			return

		for row in self.packaging_used:

			stock_qty = frappe.db.get_value("Packaging Material", row.material, "stock_qty")

			if stock_qty is None:
				frappe.throw(f"Packaging Material {row.material} was not found.")

			
			new_stock_qty = stock_qty - row.quantity

			frappe.db.set_value("Packaging Material", row.material, "stock_qty", new_stock_qty)

		receipt = frappe.get_doc({
			"doctype": "Delivery Receipt",

			"delivery_order": self.name,

			"customer_name": self.customer_name,

			"delivery_fee": self.delivery_fee,

			"packaging_total": self.packaging_total,

			"total_amount": self.final_amount,

			"payment_status": self.payment_status
		})

		receipt.insert(ignore_permissions=True)

		frappe.enqueue("dashpoint.api.send_delivery_confirmation", delivery_order_name=self.name, queue="short")


	def on_cancel(self):
		
		if self.status != "Cancelled":
			return

		for row in self.packaging_used:

			stock_qty = frappe.db.get_value("Packaging Material", row.material, "stock_qty")

			if stock_qty is None:
				continue

			new_stock_qty = stock_qty + row.quantity

			frappe.db.set_value("Packaging Material", row.material, "stock_qty", new_stock_qty)

		
		receipt_name = frappe.db.get_value("Delivery Receipt", {"delivery_order": self.name}, "name")
		
		if receipt_name:

			receipt = frappe.get_doc("Delivery Receipt", receipt_name)

			if receipt.docstatus == 1:
				receipt.cancel()
    
	def on_trash(self):
		if self.status not in ["Cancelled", "Draft"]:
			frappe.throw("Delivery Order cannot be deleted unless status is Draft or Cancelled.")
   
	def before_print(self, print_settings):
		self.print_summary = f"{self.customer_name} - {self.delivery_zone}"

	def on_update(self):
		pass

	