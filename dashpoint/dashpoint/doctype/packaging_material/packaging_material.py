# Copyright (c) 2026, Guruprasad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class PackagingMaterial(Document):
	# def autoname(self):
	# 	self.name = self.material_code.upper()
	def autoname(self):
		self.material_code = self.material_code.upper()

		self.name = make_autoname(
			f"{self.material_code}-.#####"
		)
	def validate(self):
		if self.charge_to_customer < self.unit_cost:
			frappe.throw("customer charge must be equal of greater than unit cost")

	def on_update(self):
		threshold = frappe.db.get_value(
			"Dispatch Settings",
			None,
			"low_stock_threshold"
		)

		if threshold is not None and self.stock_qty <= threshold:
			frappe.msgprint(
				f"Low stock warning: {self.material_name} "
				f"has only {self.stock_qty} units."
			)