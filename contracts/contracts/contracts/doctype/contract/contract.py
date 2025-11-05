# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, nowdate

class Contract(Document):
	def validate(self):
		self.validate_dates()
		self.update_status()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw("End Date cannot be before Start Date")

	def update_status(self):
		"""Update contract status based on dates"""
		if self.status == "Draft":
			return

		today = getdate(nowdate())
		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)

		if today < start_date:
			self.status = "Draft"
		elif start_date <= today <= end_date:
			if self.status != "Terminated":
				self.status = "Active"
		elif today > end_date:
			if self.status not in ["Terminated", "Renewed"]:
				self.status = "Expired"

	def on_update(self):
		"""Check if notification needs to be sent"""
		self.check_expiry_notification()

	def check_expiry_notification(self):
		"""Send notification before contract expires"""
		if self.status == "Active" and self.notification_days:
			days_to_expiry = (getdate(self.end_date) - getdate(nowdate())).days
			if days_to_expiry == self.notification_days:
				self.send_expiry_notification()

	def send_expiry_notification(self):
		"""Send email notification for contract expiry"""
		# This can be customized based on requirements
		pass
