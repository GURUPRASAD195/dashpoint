# Copyright (c) 2026, Guruprasad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class PackagingMaterial(Document):
	def autoname(self):
		self.name = self.material_code.upper()

	def validate(self):
		if self.charge_to_customer < self.unit_cost:
			frappe.throw("customer charge must be equal of greater than unit cost")