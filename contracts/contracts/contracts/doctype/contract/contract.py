# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, add_months, add_years, nowdate, now_datetime, flt, cint
from datetime import datetime
import json


class Contract(Document):
	def validate(self):
		"""Validate contract data before saving"""
		self.validate_dates()
		self.validate_financial()
		self.validate_approval()
		self.validate_renewal()
		self.calculate_duration()
		self.calculate_currency_values()
		self.update_status()

	def before_save(self):
		"""Actions before saving the contract"""
		self.create_version_history()

	def on_update(self):
		"""Actions after updating the contract"""
		self.check_expiry_notification()
		self.check_renewal_notification()
		self.check_overdue_items()

	def on_submit(self):
		"""Actions when contract is submitted"""
		if self.requires_approval and self.approval_status != "Approved":
			self.status = "Pending Approval"
		else:
			self.status = "Approved"

	def validate_dates(self):
		"""Validate all date fields"""
		# End date must be after start date
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw(_("End Date cannot be before Start Date"))

		# Effective date validation
		if self.effective_date and self.start_date:
			if getdate(self.effective_date) > getdate(self.start_date):
				frappe.msgprint(_("Effective Date is after Start Date"), alert=True)

		# Signing date validation
		if self.signing_date and self.start_date:
			if getdate(self.signing_date) > getdate(self.start_date):
				frappe.msgprint(_("Signing Date is after Start Date"), alert=True)

	def calculate_duration(self):
		"""Calculate contract duration in days"""
		if self.start_date and self.end_date:
			start = getdate(self.start_date)
			end = getdate(self.end_date)
			self.duration_days = (end - start).days

	def validate_financial(self):
		"""Validate financial data"""
		# Contract value must be positive
		if self.contract_value and self.contract_value < 0:
			frappe.throw(_("Contract Value must be positive"))

		# Validate payment schedule
		if self.payment_schedule:
			total_payment = sum([flt(row.amount) for row in self.payment_schedule])
			if self.contract_value and abs(total_payment - self.contract_value) > 0.01:
				frappe.msgprint(
					_("Total payment schedule amount ({0}) does not match contract value ({1})").format(
						total_payment, self.contract_value
					),
					alert=True
				)

		# Validate advance payment percentage
		if self.advance_payment_required and self.advance_payment_percentage:
			if self.advance_payment_percentage < 0 or self.advance_payment_percentage > 100:
				frappe.throw(_("Advance Payment Percentage must be between 0 and 100"))

	def calculate_currency_values(self):
		"""Calculate contract value in company currency"""
		if self.contract_value and self.exchange_rate:
			self.contract_value_in_company_currency = flt(self.contract_value * self.exchange_rate)

	def validate_approval(self):
		"""Validate approval requirements"""
		if self.requires_approval:
			# If approved, approved_by and approved_on must be set
			if self.approval_status == "Approved":
				if not self.approved_by:
					frappe.throw(_("Approved By is required when approval status is Approved"))
				if not self.approved_on:
					self.approved_on = nowdate()

			# If rejected, comments are required
			if self.approval_status == "Rejected" and not self.approval_comments:
				frappe.throw(_("Approval Comments are required when rejecting a contract"))

	def validate_renewal(self):
		"""Validate renewal settings"""
		if self.auto_renew:
			if not self.renewal_period:
				frappe.throw(_("Renewal Period is required when Auto Renew is enabled"))

			if self.max_renewals and self.renewal_count >= self.max_renewals:
				frappe.msgprint(_("Contract has reached maximum number of renewals"), alert=True)

	def update_status(self):
		"""Update contract status based on dates and conditions"""
		if self.docstatus == 0:  # Draft
			if self.status not in ["Draft", "Pending Approval", "Approved", "Rejected"]:
				return

		if self.docstatus == 1:  # Submitted
			today = getdate(nowdate())
			start_date = getdate(self.start_date)
			end_date = getdate(self.end_date)

			# Check if contract should be active
			if start_date <= today <= end_date:
				if self.status not in ["Terminated", "On Hold"] and self.approval_status == "Approved":
					self.status = "Active"
			# Check if contract has expired
			elif today > end_date:
				if self.status not in ["Terminated", "Renewed"]:
					self.status = "Expired"

	def create_version_history(self):
		"""Create version history entry on changes"""
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc:
				changes = self.get_doc_changes()
				if changes:
					version_entry = {
						"version_number": self.document_version,
						"version_date": now_datetime(),
						"changed_by": frappe.session.user,
						"change_summary": self.get_change_summary(changes)
					}
					self.append("version_history", version_entry)

	def get_change_summary(self, changes):
		"""Generate a summary of changes"""
		summary = []
		for field, values in changes.items():
			if field not in ["modified", "modified_by"]:
				summary.append(f"{field}: {values[0]} → {values[1]}")
		return "; ".join(summary[:5])  # Limit to first 5 changes

	def get_doc_changes(self):
		"""Get changes between current and previous version"""
		old_doc = self.get_doc_before_save()
		if not old_doc:
			return {}

		changes = {}
		for field in self.meta.get_fieldnames():
			if field in ["modified", "modified_by", "version_history"]:
				continue
			old_value = old_doc.get(field)
			new_value = self.get(field)
			if old_value != new_value:
				changes[field] = (old_value, new_value)
		return changes

	def check_expiry_notification(self):
		"""Check if contract expiry notification should be sent"""
		if not self.expiry_notification_enabled:
			return

		if self.status not in ["Active", "Approved"]:
			return

		today = getdate(nowdate())
		end_date = getdate(self.end_date)
		days_to_expiry = (end_date - today).days

		# Send notification at configured days before expiry
		if days_to_expiry == self.notification_days:
			self.send_expiry_notification()

		# Also send at 90, 60, 30, 7 days if enabled
		if days_to_expiry in [90, 60, 30, 7]:
			self.send_expiry_notification()

	def send_expiry_notification(self):
		"""Send contract expiry notification"""
		recipients = []
		if self.assigned_to:
			recipients.append(self.assigned_to)

		# Add contract manager role users
		contract_managers = frappe.get_all(
			"Has Role",
			filters={"role": "Contract Manager", "parenttype": "User"},
			fields=["parent"]
		)
		for manager in contract_managers:
			recipients.append(manager.parent)

		if not recipients:
			return

		subject = _("Contract Expiring Soon: {0}").format(self.contract_name)
		message = _("The contract <b>{0}</b> is expiring on {1}. Please review and take necessary action.").format(
			self.contract_name, self.end_date
		)

		frappe.sendmail(
			recipients=list(set(recipients)),
			subject=subject,
			message=message,
			reference_doctype=self.doctype,
			reference_name=self.name
		)

	def check_renewal_notification(self):
		"""Check if renewal notification should be sent"""
		if not self.auto_renew:
			return

		if self.status != "Active":
			return

		today = getdate(nowdate())
		end_date = getdate(self.end_date)
		days_to_expiry = (end_date - today).days

		if days_to_expiry == self.renewal_notification_days:
			self.send_renewal_notification()

	def send_renewal_notification(self):
		"""Send contract renewal notification"""
		recipients = []
		if self.assigned_to:
			recipients.append(self.assigned_to)

		if not recipients:
			return

		subject = _("Contract Renewal Due: {0}").format(self.contract_name)
		message = _("The contract <b>{0}</b> is set for auto-renewal. Please review the renewal terms.").format(
			self.contract_name
		)

		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			message=message,
			reference_doctype=self.doctype,
			reference_name=self.name
		)

	def check_overdue_items(self):
		"""Check for overdue obligations, deliverables, and payments"""
		today = getdate(nowdate())

		# Check overdue payments
		for payment in self.payment_schedule:
			if payment.payment_status == "Pending" and getdate(payment.due_date) < today:
				payment.payment_status = "Overdue"

		# Check overdue obligations
		for obligation in self.obligations:
			if obligation.status == "Pending" and obligation.due_date and getdate(obligation.due_date) < today:
				obligation.status = "Overdue"

		# Check delayed deliverables
		for deliverable in self.deliverables:
			if deliverable.status not in ["Completed", "Cancelled"] and getdate(deliverable.due_date) < today:
				deliverable.status = "Delayed"

	@frappe.whitelist()
	def create_amendment(self, amendment_data):
		"""Create an amendment to the contract"""
		if self.status not in ["Active", "Approved"]:
			frappe.throw(_("Only Active or Approved contracts can be amended"))

		amendment = frappe._dict(amendment_data)

		# Auto-generate amendment number
		existing_amendments = len(self.amendments)
		amendment_number = f"AMD-{existing_amendments + 1:03d}"

		self.append("amendments", {
			"amendment_number": amendment_number,
			"amendment_date": nowdate(),
			"amendment_type": amendment.get("amendment_type"),
			"description": amendment.get("description"),
			"previous_value": amendment.get("previous_value"),
			"new_value": amendment.get("new_value"),
			"effective_from": amendment.get("effective_from") or nowdate()
		})

		# Increment document version
		current_version = float(self.document_version or "1.0")
		self.document_version = str(current_version + 0.1)

		self.save()
		frappe.msgprint(_("Amendment {0} created successfully").format(amendment_number))

	@frappe.whitelist()
	def renew_contract(self):
		"""Create a renewed contract"""
		if not self.auto_renew:
			frappe.throw(_("This contract is not set for auto-renewal"))

		if self.max_renewals and self.renewal_count >= self.max_renewals:
			frappe.throw(_("Contract has reached maximum number of renewals"))

		# Create a new contract based on this one
		new_contract = frappe.copy_doc(self)

		# Update dates based on renewal period
		new_start_date = add_days(getdate(self.end_date), 1)
		if self.renewal_period == "1 Month":
			new_end_date = add_months(new_start_date, 1)
		elif self.renewal_period == "3 Months":
			new_end_date = add_months(new_start_date, 3)
		elif self.renewal_period == "6 Months":
			new_end_date = add_months(new_start_date, 6)
		elif self.renewal_period == "1 Year":
			new_end_date = add_years(new_start_date, 1)
		elif self.renewal_period == "2 Years":
			new_end_date = add_years(new_start_date, 2)
		elif self.renewal_period == "3 Years":
			new_end_date = add_years(new_start_date, 3)
		else:
			new_end_date = add_years(new_start_date, 1)

		new_contract.start_date = new_start_date
		new_contract.end_date = new_end_date
		new_contract.status = "Draft"
		new_contract.renewal_count = self.renewal_count + 1
		new_contract.master_agreement = self.master_agreement or self.name

		# Clear certain fields
		new_contract.approved_by = None
		new_contract.approved_on = None
		new_contract.approval_status = "Pending"

		new_contract.insert()

		# Update current contract
		self.status = "Renewed"
		self.save()

		# Link renewed contract
		self.append("related_contracts", {
			"contract": new_contract.name,
			"relationship_type": "Renewal",
			"description": f"Renewed from {self.name}"
		})
		self.save()

		frappe.msgprint(_("Renewed contract {0} created successfully").format(new_contract.name))
		return new_contract.name

	@frappe.whitelist()
	def terminate_contract(self, termination_reason):
		"""Terminate the contract"""
		if self.status not in ["Active", "Approved"]:
			frappe.throw(_("Only Active or Approved contracts can be terminated"))

		self.status = "Terminated"
		self.add_comment("Comment", _("Contract terminated. Reason: {0}").format(termination_reason))
		self.save()
		frappe.msgprint(_("Contract terminated successfully"))

	@frappe.whitelist()
	def put_on_hold(self, hold_reason):
		"""Put contract on hold"""
		if self.status != "Active":
			frappe.throw(_("Only Active contracts can be put on hold"))

		self.status = "On Hold"
		self.add_comment("Comment", _("Contract put on hold. Reason: {0}").format(hold_reason))
		self.save()
		frappe.msgprint(_("Contract put on hold"))

	@frappe.whitelist()
	def resume_contract(self):
		"""Resume contract from hold"""
		if self.status != "On Hold":
			frappe.throw(_("Only contracts on hold can be resumed"))

		self.status = "Active"
		self.add_comment("Comment", _("Contract resumed from hold"))
		self.save()
		frappe.msgprint(_("Contract resumed"))

	def get_dashboard_data(self):
		"""Get data for contract dashboard"""
		return {
			"total_value": flt(self.contract_value),
			"paid_amount": self.get_total_paid_amount(),
			"pending_amount": self.get_total_pending_amount(),
			"overdue_amount": self.get_total_overdue_amount(),
			"deliverables_completion": self.get_deliverables_completion_rate(),
			"obligations_completion": self.get_obligations_completion_rate(),
			"days_remaining": self.get_days_remaining(),
			"milestone_achievement": self.get_milestone_achievement_rate()
		}

	def get_total_paid_amount(self):
		"""Calculate total paid amount"""
		return sum([flt(row.amount) for row in self.payment_schedule if row.payment_status == "Paid"])

	def get_total_pending_amount(self):
		"""Calculate total pending amount"""
		return sum([flt(row.amount) for row in self.payment_schedule if row.payment_status == "Pending"])

	def get_total_overdue_amount(self):
		"""Calculate total overdue amount"""
		return sum([flt(row.amount) for row in self.payment_schedule if row.payment_status == "Overdue"])

	def get_deliverables_completion_rate(self):
		"""Calculate deliverables completion rate"""
		if not self.deliverables:
			return 0
		total = len(self.deliverables)
		completed = len([d for d in self.deliverables if d.status == "Completed"])
		return (completed / total) * 100 if total > 0 else 0

	def get_obligations_completion_rate(self):
		"""Calculate obligations completion rate"""
		if not self.obligations:
			return 0
		total = len(self.obligations)
		completed = len([o for o in self.obligations if o.status == "Completed"])
		return (completed / total) * 100 if total > 0 else 0

	def get_milestone_achievement_rate(self):
		"""Calculate milestone achievement rate"""
		if not self.milestones:
			return 0
		total = len(self.milestones)
		achieved = len([m for m in self.milestones if m.achieved])
		return (achieved / total) * 100 if total > 0 else 0

	def get_days_remaining(self):
		"""Calculate days remaining until contract end"""
		if self.status not in ["Active", "Approved"]:
			return 0
		today = getdate(nowdate())
		end_date = getdate(self.end_date)
		return (end_date - today).days if end_date > today else 0


# Scheduled tasks
def check_expiring_contracts():
	"""Daily scheduled task to check for expiring contracts"""
	contracts = frappe.get_all(
		"Contract",
		filters={
			"status": ["in", ["Active", "Approved"]],
			"docstatus": 1,
			"expiry_notification_enabled": 1
		},
		fields=["name"]
	)

	for contract_name in contracts:
		try:
			contract = frappe.get_doc("Contract", contract_name.name)
			contract.check_expiry_notification()
		except Exception as e:
			frappe.log_error(f"Error checking expiry for contract {contract_name.name}: {str(e)}")


def auto_renew_contracts():
	"""Daily scheduled task to auto-renew contracts"""
	today = getdate(nowdate())

	contracts = frappe.get_all(
		"Contract",
		filters={
			"status": "Active",
			"docstatus": 1,
			"auto_renew": 1,
			"end_date": today
		},
		fields=["name"]
	)

	for contract_name in contracts:
		try:
			contract = frappe.get_doc("Contract", contract_name.name)
			contract.renew_contract()
		except Exception as e:
			frappe.log_error(f"Error auto-renewing contract {contract_name.name}: {str(e)}")


def update_contract_statuses():
	"""Daily scheduled task to update contract statuses"""
	contracts = frappe.get_all(
		"Contract",
		filters={
			"status": ["in", ["Active", "Approved"]],
			"docstatus": 1
		},
		fields=["name"]
	)

	for contract_name in contracts:
		try:
			contract = frappe.get_doc("Contract", contract_name.name)
			contract.update_status()
			contract.check_overdue_items()
			contract.save()
		except Exception as e:
			frappe.log_error(f"Error updating status for contract {contract_name.name}: {str(e)}")
