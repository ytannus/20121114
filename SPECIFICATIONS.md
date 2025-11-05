# Frappe Contracts App - Technical Specifications

## 1. Overview

The Frappe Contracts app is a comprehensive contract lifecycle management system designed to handle all aspects of contract creation, approval, execution, monitoring, and renewal within the Frappe/ERPNext ecosystem.

### 1.1 Objectives

- Centralized contract repository
- Automated contract lifecycle management
- Compliance tracking and reporting
- Integration with existing Frappe DocTypes (Customer, Supplier, Employee, etc.)
- Automated notifications and reminders
- Document version control
- Audit trail for all contract changes
- Advanced search and filtering capabilities
- Reporting and analytics dashboard

### 1.2 Scope

This application covers:
- Contract creation and management
- Multi-party contracts
- Contract templates
- Approval workflows
- Document attachments and versioning
- Contract renewal management
- Obligation tracking
- Milestone and payment schedules
- Compliance monitoring
- Reporting and analytics

## 2. User Roles and Permissions

### 2.1 System Manager
- Full access to all features
- System configuration
- User role management
- Access to all contracts

### 2.2 Contract Manager
- Create, edit, and manage all contracts
- Approve contracts (if designated)
- Access to all contracts
- Generate reports
- Configure contract templates
- Manage contract workflows

### 2.3 Contract Creator
- Create new contracts
- Edit draft contracts
- Submit contracts for approval
- View assigned contracts
- Upload documents

### 2.4 Contract Approver
- Review contracts
- Approve/reject contracts
- Add approval comments
- View contracts pending approval

### 2.5 Contract Viewer
- Read-only access to contracts
- View contract history
- Download contract documents
- View reports (limited)

### 2.6 Department User
- View contracts related to their department
- Create contracts for their department
- Track department obligations

## 3. DocTypes Specification

### 3.1 Contract (Main DocType)

**Purpose**: Core document for managing individual contracts

**Naming**: Auto-numbered with configurable series (CONTRACT-.YYYY.-.####)

**Fields**:

#### Basic Information
- `contract_name` (Data, Required): Display name of the contract
- `contract_id` (Read Only): Auto-generated unique identifier
- `naming_series` (Select, Required): CONTRACT-.YYYY.-
- `contract_type` (Link to Contract Type, Required): Type of contract
- `status` (Select, Required): Draft, Pending Approval, Active, Expired, Terminated, Renewed, On Hold
- `priority` (Select): Low, Medium, High, Critical
- `department` (Link to Department): Owning department
- `cost_center` (Link to Cost Center): Associated cost center
- `project` (Link to Project): Associated project (if any)

#### Party Information
- `party_type` (Link to DocType): Customer, Supplier, Employee, Company, etc.
- `party` (Dynamic Link): The actual party
- `party_name` (Data, Read Only): Fetched from party
- `party_address` (Link to Address): Party address
- `party_contact` (Link to Contact): Party contact person
- `additional_parties` (Table): Contract Additional Party (for multi-party contracts)

#### Duration and Dates
- `start_date` (Date, Required): Contract start date
- `end_date` (Date, Required): Contract end date
- `duration_days` (Int, Read Only): Auto-calculated duration
- `signing_date` (Date): Date when contract was signed
- `effective_date` (Date): Date when contract becomes effective
- `notice_period_days` (Int): Notice period for termination
- `expiry_notification_enabled` (Check): Enable expiry notifications
- `notification_days` (Int): Days before expiry to notify

#### Financial Details
- `contract_value` (Currency): Total contract value
- `currency` (Link to Currency): Contract currency
- `contract_value_in_company_currency` (Currency, Read Only): Converted value
- `exchange_rate` (Float): Currency exchange rate
- `tax_category` (Link to Tax Category): Tax category
- `payment_terms` (Link to Payment Terms Template): Payment terms
- `payment_schedule` (Table): Contract Payment Schedule (child table)
- `billing_cycle` (Select): One-time, Monthly, Quarterly, Semi-Annual, Annual
- `advance_payment_required` (Check): Advance payment flag
- `advance_payment_percentage` (Percent): Advance payment percentage

#### Contract Terms
- `contract_terms` (Text Editor): Detailed contract terms
- `description` (Text): Brief description
- `scope_of_work` (Text Editor): Scope of work description
- `deliverables` (Table): Contract Deliverable (child table)
- `obligations` (Table): Contract Obligation (child table)
- `special_clauses` (Text Editor): Special clauses or conditions
- `termination_clause` (Text Editor): Termination conditions
- `confidentiality_clause` (Text Editor): Confidentiality terms
- `dispute_resolution` (Text Editor): Dispute resolution mechanism

#### Renewal Settings
- `auto_renew` (Check): Enable auto-renewal
- `renewal_period` (Select): 1 Month, 3 Months, 6 Months, 1 Year, 2 Years, 3 Years
- `renewal_notification_days` (Int): Days before renewal date to notify
- `renewal_terms` (Text): Renewal terms and conditions
- `max_renewals` (Int): Maximum number of renewals allowed
- `renewal_count` (Int, Read Only): Current renewal count

#### Approval and Signatory
- `requires_approval` (Check): Requires approval workflow
- `approval_status` (Select): Pending, Approved, Rejected
- `approved_by` (Link to User): Approving authority
- `approved_on` (Date): Approval date
- `approval_comments` (Text): Approval comments
- `company_signatory` (Link to Employee): Company signatory
- `company_signatory_designation` (Data): Signatory designation
- `party_signatory_name` (Data): Party signatory name
- `party_signatory_designation` (Data): Party signatory designation
- `witness_1` (Data): First witness name
- `witness_2` (Data): Second witness name

#### Compliance and Risk
- `compliance_requirements` (Table): Contract Compliance (child table)
- `risk_level` (Select): Low, Medium, High, Critical
- `risk_assessment` (Text): Risk assessment details
- `insurance_required` (Check): Insurance requirement flag
- `insurance_details` (Text): Insurance details
- `regulatory_approvals` (Table): Contract Regulatory Approval (child table)

#### Document Management
- `attachments` (Table): Contract Attachment (child table)
- `document_version` (Data, Read Only): Current version
- `version_history` (Table): Contract Version (child table)
- `master_agreement` (Link to Contract): Link to master contract
- `related_contracts` (Table): Related Contract (child table)

#### Tracking and Monitoring
- `milestones` (Table): Contract Milestone (child table)
- `performance_metrics` (Table): Contract Performance Metric (child table)
- `reviews` (Table): Contract Review (child table)
- `amendments` (Table): Contract Amendment (child table)
- `next_review_date` (Date): Next review date
- `review_frequency` (Select): Monthly, Quarterly, Semi-Annual, Annual

#### Internal Notes
- `internal_notes` (Text): Internal notes (not visible to parties)
- `assigned_to` (Link to User): Person responsible
- `tags` (Data): Tags for categorization

#### Audit Fields (Auto-populated)
- `created_by` (Link to User, Read Only)
- `creation_date` (DateTime, Read Only)
- `modified_by` (Link to User, Read Only)
- `modified_date` (DateTime, Read Only)

**Validations**:
- End date must be after start date
- Contract value must be positive
- If auto-renew is enabled, renewal period is required
- Approval status must be "Approved" before contract can be activated
- Notice period must be less than contract duration

**Business Logic**:
- Auto-calculate duration_days from start and end dates
- Auto-update status based on dates (Draft → Active → Expired)
- Send notifications before contract expiry
- Send notifications for upcoming milestones
- Send notifications for pending obligations
- Auto-create renewal contract when auto-renew is enabled
- Track contract amendments and maintain version history
- Calculate contract value in company currency using exchange rate

### 3.2 Contract Type

**Purpose**: Define different types of contracts

**Fields**:
- `contract_type_name` (Data, Required): Type name
- `description` (Text): Description
- `default_duration_days` (Int): Default contract duration
- `requires_approval` (Check): Approval required by default
- `default_terms` (Text Editor): Default contract terms template
- `approval_workflow` (Link to Workflow): Associated workflow
- `notification_template` (Link to Email Template): Default notification template
- `is_active` (Check): Active status

### 3.3 Contract Template

**Purpose**: Predefined contract templates for quick creation

**Fields**:
- `template_name` (Data, Required): Template name
- `contract_type` (Link to Contract Type, Required)
- `template_content` (Text Editor, Required): Template content with placeholders
- `description` (Text): Template description
- `default_currency` (Link to Currency)
- `default_payment_terms` (Link to Payment Terms Template)
- `default_duration_days` (Int)
- `standard_clauses` (Table): Standard Clause (child table)
- `required_fields` (Small Text): List of required fields
- `is_active` (Check)

### 3.4 Contract Attachment (Child Table)

**Purpose**: Store multiple documents related to a contract

**Fields**:
- `document_name` (Data, Required): Document name
- `attachment` (Attach, Required): File attachment
- `document_type` (Select): Main Contract, Amendment, Annexure, Correspondence, Invoice, Other
- `version` (Data): Document version
- `uploaded_by` (Link to User): Uploader
- `uploaded_on` (DateTime): Upload timestamp
- `description` (Small Text): Document description
- `is_signed` (Check): Signed document flag
- `is_latest` (Check): Latest version flag

### 3.5 Contract Additional Party (Child Table)

**Purpose**: Support multi-party contracts

**Fields**:
- `party_type` (Link to DocType, Required)
- `party` (Dynamic Link, Required)
- `party_name` (Data, Read Only)
- `role` (Select): Co-signer, Guarantor, Beneficiary, Witness, Other
- `signatory_name` (Data)
- `signatory_designation` (Data)
- `signature_date` (Date)
- `signature_status` (Select): Pending, Signed, Declined

### 3.6 Contract Payment Schedule (Child Table)

**Purpose**: Define payment milestones and schedules

**Fields**:
- `payment_term` (Data, Required): Payment term description
- `due_date` (Date, Required): Payment due date
- `amount` (Currency, Required): Payment amount
- `percentage_of_total` (Percent): Percentage of total contract value
- `invoice_reference` (Link to Sales Invoice): Reference to invoice
- `payment_status` (Select): Pending, Paid, Overdue, Waived
- `payment_date` (Date): Actual payment date
- `payment_reference` (Data): Payment reference number
- `notes` (Text): Payment notes

### 3.7 Contract Deliverable (Child Table)

**Purpose**: Track contract deliverables

**Fields**:
- `deliverable_name` (Data, Required): Deliverable name
- `description` (Text): Detailed description
- `due_date` (Date, Required): Expected completion date
- `responsible_party` (Select): Company, Party, Other
- `assigned_to` (Link to User): Person responsible
- `status` (Select): Not Started, In Progress, Completed, Delayed, Cancelled
- `completion_date` (Date): Actual completion date
- `completion_percentage` (Percent): Progress percentage
- `notes` (Text): Notes

### 3.8 Contract Obligation (Child Table)

**Purpose**: Track obligations for both parties

**Fields**:
- `obligation_name` (Data, Required): Obligation name
- `description` (Text): Detailed description
- `obligated_party` (Select): Company, Party, Both, Other
- `obligation_type` (Select): Compliance, Reporting, Payment, Delivery, Maintenance, Other
- `due_date` (Date): Due date
- `frequency` (Select): One-time, Daily, Weekly, Monthly, Quarterly, Annual
- `status` (Select): Pending, In Progress, Completed, Overdue, Waived
- `completion_date` (Date): Completion date
- `assigned_to` (Link to User): Person responsible
- `reminder_enabled` (Check): Enable reminders
- `reminder_days_before` (Int): Days before due date to remind

### 3.9 Contract Compliance (Child Table)

**Purpose**: Track compliance requirements

**Fields**:
- `compliance_item` (Data, Required): Compliance requirement
- `description` (Text): Detailed description
- `regulatory_body` (Data): Regulatory authority
- `due_date` (Date): Compliance due date
- `status` (Select): Compliant, Non-Compliant, In Progress, Not Applicable
- `evidence_document` (Attach): Supporting document
- `verified_by` (Link to User): Verifying authority
- `verification_date` (Date): Verification date
- `notes` (Text): Compliance notes

### 3.10 Contract Milestone (Child Table)

**Purpose**: Track contract milestones

**Fields**:
- `milestone_name` (Data, Required): Milestone name
- `description` (Text): Milestone description
- `target_date` (Date, Required): Target completion date
- `actual_date` (Date): Actual completion date
- `status` (Select): Not Started, In Progress, Completed, Delayed
- `payment_linked` (Check): Linked to payment
- `payment_percentage` (Percent): Payment percentage
- `completion_criteria` (Text): Completion criteria
- `achieved` (Check): Milestone achieved flag

### 3.11 Contract Amendment (Child Table)

**Purpose**: Track all amendments to the contract

**Fields**:
- `amendment_number` (Data, Required): Amendment number
- `amendment_date` (Date, Required): Date of amendment
- `amendment_type` (Select): Scope Change, Duration Extension, Value Change, Terms Modification, Other
- `description` (Text, Required): Amendment description
- `previous_value` (Text): Previous value
- `new_value` (Text): New value
- `approved_by` (Link to User): Approver
- `approval_date` (Date): Approval date
- `document` (Attach): Amendment document
- `effective_from` (Date): Effective date

### 3.12 Contract Version (Child Table)

**Purpose**: Maintain version history

**Fields**:
- `version_number` (Data, Required): Version number
- `version_date` (DateTime, Required): Version timestamp
- `changed_by` (Link to User, Required): User who made changes
- `change_summary` (Text): Summary of changes
- `document_snapshot` (Long Text): JSON snapshot of contract state

### 3.13 Contract Review (Child Table)

**Purpose**: Track periodic contract reviews

**Fields**:
- `review_date` (Date, Required): Review date
- `reviewed_by` (Link to User, Required): Reviewer
- `review_type` (Select): Scheduled, Ad-hoc, Audit, Performance
- `findings` (Text): Review findings
- `recommendations` (Text): Recommendations
- `action_items` (Text): Action items
- `next_review_date` (Date): Next scheduled review
- `status` (Select): Scheduled, Completed, Cancelled

### 3.14 Contract Performance Metric (Child Table)

**Purpose**: Track contract performance KPIs

**Fields**:
- `metric_name` (Data, Required): KPI name
- `description` (Text): Metric description
- `target_value` (Float): Target value
- `actual_value` (Float): Actual value
- `unit_of_measure` (Data): Unit (%, $, days, etc.)
- `measurement_date` (Date): Measurement date
- `status` (Select): On Track, At Risk, Below Target, Above Target
- `notes` (Text): Performance notes

### 3.15 Contract Regulatory Approval (Child Table)

**Purpose**: Track required regulatory approvals

**Fields**:
- `approval_name` (Data, Required): Approval name
- `regulatory_body` (Data): Regulatory authority
- `application_date` (Date): Application submission date
- `approval_date` (Date): Approval received date
- `approval_reference` (Data): Reference number
- `status` (Select): Not Applied, Applied, Approved, Rejected, Expired
- `expiry_date` (Date): Approval expiry date
- `document` (Attach): Approval document
- `notes` (Text): Notes

### 3.16 Related Contract (Child Table)

**Purpose**: Link related contracts

**Fields**:
- `contract` (Link to Contract, Required): Related contract
- `relationship_type` (Select): Parent, Child, Amendment, Renewal, Superseded By, Related
- `description` (Text): Relationship description

## 4. Workflow Specifications

### 4.1 Contract Approval Workflow

**States**:
1. Draft
2. Pending Approval
3. Approved
4. Rejected
5. Active
6. On Hold
7. Expired
8. Terminated
9. Renewed

**Transitions**:
- Draft → Pending Approval (Submit)
- Pending Approval → Approved (Approve)
- Pending Approval → Rejected (Reject)
- Pending Approval → Draft (Cancel Submission)
- Approved → Active (Activate)
- Active → On Hold (Put On Hold)
- On Hold → Active (Resume)
- Active → Terminated (Terminate)
- Active → Expired (Auto - based on end date)
- Active → Renewed (Renew)
- Rejected → Draft (Revise)

**Approval Rules**:
- Contracts < $10,000: Requires Manager approval
- Contracts $10,000 - $100,000: Requires Senior Manager approval
- Contracts > $100,000: Requires Director approval
- High-risk contracts: Requires Legal team approval
- Multi-year contracts: Requires CFO approval

### 4.2 Amendment Workflow

**Process**:
1. Create amendment record
2. Submit for approval
3. Approve amendment
4. Update contract
5. Create new version
6. Notify stakeholders

## 5. Automated Processes

### 5.1 Scheduled Tasks

**Daily Tasks**:
- Check for contracts expiring within notification period
- Check for overdue obligations
- Check for upcoming milestones
- Check for overdue payments
- Update contract statuses based on dates

**Weekly Tasks**:
- Send weekly digest of contracts requiring attention
- Generate pending approvals report
- Check compliance deadlines

**Monthly Tasks**:
- Generate monthly contract summary report
- Archive expired contracts (after retention period)
- Review auto-renewal eligible contracts

### 5.2 Email Notifications

**Triggers**:
- Contract created → Notify assigned user
- Contract submitted for approval → Notify approvers
- Contract approved → Notify creator and stakeholders
- Contract rejected → Notify creator with comments
- Contract activated → Notify all parties
- X days before expiry → Notify contract manager and stakeholders
- Contract expired → Notify contract manager
- Payment due → Notify finance team
- Obligation due → Notify responsible person
- Milestone approaching → Notify project team
- Amendment created → Notify approvers
- Compliance deadline approaching → Notify compliance officer

## 6. Reports and Analytics

### 6.1 Standard Reports

1. **Contract Register**
   - All contracts with key details
   - Filterable by status, type, party, dates
   - Export to Excel/PDF

2. **Expiring Contracts Report**
   - Contracts expiring in next 30/60/90 days
   - Renewal recommendations

3. **Contract Value Analysis**
   - Total contract values by type, party, department
   - Year-over-year comparison
   - Value by status

4. **Obligation Tracking Report**
   - All pending obligations
   - Overdue obligations
   - Compliance status

5. **Payment Schedule Report**
   - Upcoming payments
   - Overdue payments
   - Payment history

6. **Performance Dashboard**
   - KPIs and metrics
   - Contract performance trends
   - Compliance rates

7. **Approval Status Report**
   - Pending approvals by approver
   - Average approval time
   - Rejection analysis

8. **Amendment History Report**
   - All amendments by contract
   - Amendment trends
   - Value changes analysis

### 6.2 Dashboard Widgets

1. **Contract Overview**
   - Total active contracts
   - Total contract value
   - Expiring soon count

2. **Status Distribution**
   - Pie chart of contracts by status

3. **Upcoming Actions**
   - List of contracts requiring attention
   - Pending approvals
   - Upcoming milestones

4. **Compliance Status**
   - Compliance rate
   - Overdue items

5. **Financial Summary**
   - Contract value by month
   - Payment status

## 7. Integration Requirements

### 7.1 ERPNext Integration

- Link to Customer, Supplier, Employee DocTypes
- Integration with Sales Invoice for payments
- Link to Projects for project-based contracts
- Integration with HR for employment contracts
- Cost Center and Department mapping

### 7.2 Document Management

- Support for multiple file formats
- Version control for documents
- Digital signature integration (optional)
- Document preview capability

### 7.3 Email Integration

- Send contracts via email
- Email tracking
- Email templates for notifications

## 8. Security and Permissions

### 8.1 Permission Levels

- Level 0: Read
- Level 1: Write (edit)
- Level 2: Submit
- Level 3: Cancel
- Level 4: Amend

### 8.2 Field-Level Permissions

- Financial fields: Restricted to Finance role
- Approval fields: Restricted to Approver role
- Internal notes: Not visible to external parties

### 8.3 Data Privacy

- Sensitive fields encrypted
- Audit trail for all changes
- Access logging
- GDPR compliance considerations

## 9. Validation Rules

### 9.1 Data Validation

- Date validations (end > start)
- Numeric validations (positive values)
- Required field validations
- Format validations (email, phone)

### 9.2 Business Rules

- Cannot activate contract without approval
- Cannot edit active contracts (amendments only)
- Cannot delete contracts with transactions
- Renewal count cannot exceed max renewals

## 10. Performance Requirements

### 10.1 Response Time

- Page load: < 2 seconds
- Search results: < 1 second
- Report generation: < 5 seconds

### 10.2 Scalability

- Support for 10,000+ contracts
- Support for 100+ concurrent users
- Efficient indexing for search

## 11. Backup and Recovery

- Daily automated backups
- Version history maintained for 7 years
- Point-in-time recovery capability

## 12. Future Enhancements (Phase 2)

- AI-powered contract analysis
- Natural language clause extraction
- Contract risk scoring
- Advanced analytics and predictive insights
- Mobile app for contract management
- E-signature integration
- Contract comparison tool
- OCR for contract scanning
- Blockchain for contract verification
- API for third-party integrations

## 13. Testing Requirements

### 13.1 Unit Testing

- Test all validations
- Test calculations
- Test status transitions

### 13.2 Integration Testing

- Test workflow transitions
- Test email notifications
- Test report generation

### 13.3 User Acceptance Testing

- Test all user scenarios
- Test permissions
- Test performance with production-like data

## 14. Documentation Requirements

- User manual
- Administrator guide
- API documentation
- Training materials
- Video tutorials

## 15. Deployment

### 15.1 Installation Steps

1. Get app from repository
2. Install app on Frappe site
3. Run patches and migrations
4. Configure permissions
5. Set up workflows
6. Configure email templates
7. Import master data
8. User training
9. Go live

### 15.2 Configuration Checklist

- [ ] Create Contract Types
- [ ] Create Contract Templates
- [ ] Set up Approval Workflows
- [ ] Configure Email Templates
- [ ] Set up User Roles and Permissions
- [ ] Configure Notification Rules
- [ ] Set up Report Filters
- [ ] Configure Dashboard
- [ ] Import Existing Contracts (if any)
- [ ] User Training
- [ ] Go Live

## 16. Support and Maintenance

- Bug fixes within 24 hours
- Feature requests evaluated monthly
- Regular updates and patches
- Performance monitoring
- User support via email/ticket system
