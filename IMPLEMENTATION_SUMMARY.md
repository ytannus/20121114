# Frappe Contracts App - Implementation Summary

## Overview

A comprehensive contract lifecycle management application has been successfully implemented for the Frappe/ERPNext framework. The application provides end-to-end contract management capabilities including creation, approval, execution, monitoring, renewal, and reporting.

## What Has Been Implemented

### 1. DocTypes (16 Total)

#### Main DocTypes (3)

**Contract** - The core document with 80+ fields organized in sections:
- Basic Information (name, type, status, priority, department, project)
- Party Information (dynamic linking to any DocType - Customer, Supplier, Employee, etc.)
- Additional Parties (multi-party contract support)
- Duration & Dates (start, end, signing, effective, notice period, notifications)
- Financial Details (contract value, currency, exchange rates, payment terms, billing cycle)
- Payment Schedule (multiple payment milestones with status tracking)
- Contract Terms (description, terms, scope of work, special clauses)
- Deliverables (track what must be delivered)
- Obligations (track duties for both parties with recurring support)
- Renewal Settings (auto-renewal configuration)
- Approval & Signatory (approval workflow, company and party signatories, witnesses)
- Compliance & Risk (risk assessment, insurance requirements)
- Compliance Requirements (regulatory compliance tracking)
- Regulatory Approvals (track required approvals)
- Document Management (attachments with versioning)
- Related Contracts (link parent/child/renewed contracts)
- Milestones (track major milestones with payment linkage)
- Performance Metrics (KPIs and metrics)
- Reviews (periodic contract reviews)
- Amendments (full amendment history)
- Version History (complete audit trail)
- Internal Notes (private notes)

**Contract Type** - Define contract categories with:
- Default settings (duration, approval requirements)
- Default terms templates
- Associated workflows and notification templates

**Contract Template** - Reusable contract templates with:
- Placeholder support ({party_name}, {start_date}, etc.)
- Default settings for quick contract creation
- Required fields configuration

#### Child Table DocTypes (13)

1. **Contract Additional Party** - Support for multi-party contracts
   - Party type and dynamic linking
   - Role definition (Co-signer, Guarantor, Beneficiary, Witness)
   - Signature status tracking

2. **Contract Payment Schedule** - Payment milestone tracking
   - Payment terms and due dates
   - Amount and percentage tracking
   - Payment status (Pending, Paid, Overdue, Waived)
   - Invoice linking
   - Payment references

3. **Contract Deliverable** - Deliverable tracking
   - Description and due dates
   - Responsible party assignment
   - Status tracking (Not Started, In Progress, Completed, Delayed)
   - Completion percentage
   - Notes

4. **Contract Obligation** - Obligation tracking
   - Obligation type (Compliance, Reporting, Payment, Delivery, etc.)
   - Obligated party (Company, Party, Both, Other)
   - Frequency (One-time, Daily, Weekly, Monthly, Quarterly, Annual)
   - Recurring obligation support
   - Reminder configuration
   - Status tracking

5. **Contract Compliance** - Compliance requirement tracking
   - Regulatory body information
   - Due dates
   - Status (Compliant, Non-Compliant, In Progress, Not Applicable)
   - Evidence document attachments
   - Verification tracking

6. **Contract Milestone** - Milestone tracking
   - Target and actual dates
   - Payment linkage
   - Achievement tracking
   - Completion criteria

7. **Contract Amendment** - Amendment history
   - Amendment number (auto-generated)
   - Amendment type (Scope Change, Duration Extension, Value Change, etc.)
   - Before/after values tracking
   - Approval workflow
   - Document attachments

8. **Contract Version** - Complete version history
   - Version number and date
   - User who made changes
   - Change summary

9. **Contract Review** - Periodic review tracking
   - Review type (Scheduled, Ad-hoc, Audit, Performance)
   - Findings and recommendations
   - Action items
   - Next review date scheduling

10. **Contract Performance Metric** - KPI tracking
    - Target vs actual values
    - Unit of measure
    - Status indicators
    - Measurement dates

11. **Contract Regulatory Approval** - Regulatory approval tracking
    - Application and approval dates
    - Approval reference numbers
    - Status tracking
    - Expiry date monitoring

12. **Contract Attachment** - Document management
    - Document categorization
    - Version tracking
    - Latest version flagging
    - Upload tracking

13. **Related Contract** - Contract relationship tracking
    - Relationship types (Parent, Child, Amendment, Renewal, etc.)
    - Bidirectional relationship support

### 2. Business Logic & Automation

#### Validations
- **Date Validations**: End date must be after start date
- **Financial Validations**: Contract value must be positive; payment schedule must match contract value
- **Approval Validations**: Approver and date required when approved; comments required on rejection
- **Renewal Validations**: Renewal period required when auto-renew enabled; max renewals check

#### Auto-Calculations
- Contract duration in days
- Currency conversion to company currency
- Payment schedule totals (paid, pending, overdue)
- Deliverables completion rate
- Obligations completion rate
- Milestone achievement rate
- Days remaining until contract end

#### Status Management
- Auto-update status based on dates:
  - Draft → Active (when start date is reached and approved)
  - Active → Expired (when end date is passed)
- Manual status transitions:
  - Active ↔ On Hold
  - Active → Terminated
  - Active → Renewed
- Overdue detection for payments, obligations, and deliverables

#### Version Control
- Auto-create version history on every save
- Track field-level changes with before/after values
- Change summary generation
- Version number auto-incrementing

#### Notifications
- **Expiry Notifications**: Sent at 90, 60, 30, 7 days before expiry (configurable)
- **Renewal Notifications**: Sent at configured days before renewal
- **Recipients**: Assigned user and all Contract Managers
- Email integration with contract details

#### Contract Operations (API Methods)

1. **create_amendment()**
   - Create contract amendments
   - Auto-generate amendment numbers (AMD-001, AMD-002, etc.)
   - Track before/after values
   - Auto-increment document version

2. **renew_contract()**
   - Auto-create renewed contract
   - Calculate new dates based on renewal period
   - Link to original contract
   - Increment renewal count
   - Reset approval status

3. **terminate_contract(reason)**
   - Terminate active contracts
   - Record termination reason in comments
   - Update status to Terminated

4. **put_on_hold(reason)** / **resume_contract()**
   - Put contracts on hold temporarily
   - Resume from hold status
   - Track hold/resume reasons

5. **get_dashboard_data()**
   - Return contract metrics for dashboard
   - Financial totals and breakdowns
   - Completion rates
   - Days remaining

### 3. Scheduled Tasks (Daily Automation)

1. **check_expiring_contracts()**
   - Runs daily
   - Checks all active contracts
   - Sends expiry notifications at configured intervals
   - Logs errors for failed notifications

2. **auto_renew_contracts()**
   - Runs daily
   - Auto-renews contracts on end date
   - Creates new contract with updated dates
   - Links renewed contract to original
   - Respects max renewals limit

3. **update_contract_statuses()**
   - Runs daily
   - Updates all contract statuses based on dates
   - Marks overdue payments, obligations, deliverables
   - Logs errors for failed updates

### 4. Permissions & Roles

Four roles have been configured:

1. **System Manager**
   - Full access to all features
   - Create, read, update, delete, submit
   - System configuration access

2. **Contract Manager**
   - Full contract management access
   - Create, read, update, delete, submit
   - Can access all contracts
   - Receives expiry notifications

3. **Contract Creator**
   - Create and edit contracts
   - Submit contracts for approval
   - Cannot delete contracts
   - View own contracts

4. **Contract Viewer**
   - Read-only access
   - Export and print
   - Submit permission (for approved contracts)
   - No create/edit/delete access

## Key Features Implemented

### ✅ Contract Lifecycle Management
- Draft → Pending Approval → Approved → Active → Expired/Terminated/Renewed
- Status-based workflow with validations
- Automated status updates

### ✅ Multi-Party Contracts
- Support for unlimited additional parties
- Role assignment (Co-signer, Guarantor, Beneficiary, Witness)
- Individual signature status tracking

### ✅ Financial Management
- Multi-currency support with exchange rates
- Payment schedule with milestone tracking
- Payment status monitoring (Pending, Paid, Overdue)
- Automatic overdue detection
- Financial totals and breakdowns

### ✅ Approval Workflow
- Configurable approval requirements
- Approval status tracking
- Approver and date recording
- Rejection with mandatory comments
- Can be integrated with Frappe Workflows

### ✅ Auto-Renewal
- Configurable renewal periods (1M to 3Y)
- Maximum renewals limit
- Auto-creation of renewed contracts
- Renewal notifications
- Renewal chain tracking

### ✅ Amendment Management
- Full amendment history
- Auto-generated amendment numbers
- Before/after value tracking
- Amendment approval workflow
- Document version incrementing

### ✅ Version Control
- Complete version history
- Change tracking with user and timestamp
- Change summary generation
- Audit trail for compliance

### ✅ Obligation & Deliverable Tracking
- Multiple obligations and deliverables per contract
- Status tracking for each item
- Overdue detection
- Responsible party assignment
- Recurring obligation support
- Completion percentage tracking

### ✅ Milestone Management
- Milestone definition with target dates
- Payment linkage (payments tied to milestones)
- Achievement tracking
- Completion criteria documentation

### ✅ Compliance Management
- Compliance requirements checklist
- Regulatory approval tracking
- Evidence document attachments
- Verification workflow
- Status monitoring

### ✅ Performance Tracking
- Define KPIs and metrics
- Target vs actual tracking
- Status indicators (On Track, At Risk, Below/Above Target)
- Performance trending

### ✅ Document Management
- Multiple document attachments
- Document categorization
- Version tracking for documents
- Latest version flagging
- Upload audit trail

### ✅ Notifications & Reminders
- Expiry notifications (90, 60, 30, 7 days)
- Renewal reminders
- Obligation reminders (configurable)
- Email integration
- Multiple recipient support

### ✅ Related Contract Tracking
- Link to master agreements
- Parent/child relationships
- Amendment chains
- Renewal chains
- Related contracts

## Installation & Setup

### 1. Install the App

```bash
# Navigate to your Frappe bench
cd frappe-bench

# Get the app
bench get-app /path/to/20121114/contracts

# Install on your site
bench --site your-site-name install-app contracts

# Run migrations
bench --site your-site-name migrate

# Clear cache
bench --site your-site-name clear-cache
```

### 2. Enable Scheduled Tasks

```bash
# Make sure scheduler is enabled
bench --site your-site-name enable-scheduler
```

### 3. Set Up Roles

Navigate to: **User > Role Permission Manager**

Assign roles to users:
- Contract Manager
- Contract Creator
- Contract Viewer

### 4. Create Contract Types

Navigate to: **Contracts > Contract Type > New**

Create basic contract types:
- Service Agreement
- Purchase Agreement
- Sales Agreement
- Employment Contract
- NDA
- Consulting Agreement
- Lease Agreement

### 5. Create Contract Templates (Optional)

Navigate to: **Contracts > Contract Template > New**

Create templates for frequently used contracts with placeholders:
- `{party_name}` - Party name
- `{start_date}` - Start date
- `{end_date}` - End date
- `{contract_value}` - Contract value
- `{company}` - Company name

## Usage Examples

### Creating a New Contract

1. Navigate to **Contracts > Contract > New**
2. Fill in basic information:
   - Contract Name
   - Contract Type
   - Party Type and Party
   - Start Date and End Date
3. Add financial details:
   - Contract Value
   - Currency
   - Payment Schedule (optional)
4. Define contract terms and scope
5. Add deliverables and obligations
6. Configure renewal settings (if applicable)
7. Add signatory details
8. Attach contract documents
9. Save and Submit

### Auto-Renewal Configuration

1. Open a contract
2. Enable "Auto Renew" checkbox
3. Select "Renewal Period" (e.g., 1 Year)
4. Set "Maximum Renewals" (optional)
5. Configure "Renewal Notification Days" (default: 30)
6. Save

The system will automatically:
- Send renewal notification 30 days before expiry
- Create a new contract on the end date
- Link the new contract to the original
- Update the original contract status to "Renewed"

### Creating an Amendment

1. Open an active contract
2. Click "Create Amendment" button (custom button to be added)
3. Fill in amendment details:
   - Amendment Type
   - Description
   - Previous Value
   - New Value
4. Save

The system will:
- Auto-generate amendment number
- Add to amendments table
- Increment document version
- Create version history entry

### Tracking Contract Performance

1. Open a contract
2. Navigate to "Performance Metrics" section
3. Add metrics:
   - Metric Name (e.g., "On-time Delivery Rate")
   - Target Value (e.g., 95)
   - Unit of Measure (e.g., "%")
4. Update "Actual Value" periodically
5. System auto-updates status indicator

### Monitoring Compliance

1. Open a contract
2. Navigate to "Compliance Requirements" section
3. Add compliance items:
   - Compliance Item name
   - Regulatory Body
   - Due Date
4. Upload "Evidence Document" when compliant
5. Set "Verified By" and "Verification Date"
6. Status updates automatically

## API Reference

### Whitelisted Methods

All methods can be called via Frappe's REST API:

```javascript
// Create Amendment
frappe.call({
    method: "contracts.contracts.contracts.doctype.contract.contract.Contract.create_amendment",
    args: {
        amendment_data: {
            amendment_type: "Value Change",
            description: "Contract value increased",
            previous_value: "100,000",
            new_value: "150,000"
        }
    }
});

// Renew Contract
frappe.call({
    method: "contracts.contracts.contracts.doctype.contract.contract.Contract.renew_contract"
});

// Terminate Contract
frappe.call({
    method: "contracts.contracts.contracts.doctype.contract.contract.Contract.terminate_contract",
    args: {
        termination_reason: "Mutual agreement"
    }
});

// Put On Hold
frappe.call({
    method: "contracts.contracts.contracts.doctype.contract.contract.Contract.put_on_hold",
    args: {
        hold_reason: "Pending legal review"
    }
});

// Resume Contract
frappe.call({
    method: "contracts.contracts.contracts.doctype.contract.contract.Contract.resume_contract"
});
```

## Database Schema

### Main Tables
- `tabContract` - Main contract records
- `tabContract Type` - Contract type definitions
- `tabContract Template` - Contract templates

### Child Tables (linked to tabContract)
- `tabContract Additional Party`
- `tabContract Payment Schedule`
- `tabContract Deliverable`
- `tabContract Obligation`
- `tabContract Compliance`
- `tabContract Milestone`
- `tabContract Amendment`
- `tabContract Version`
- `tabContract Review`
- `tabContract Performance Metric`
- `tabContract Regulatory Approval`
- `tabContract Attachment`
- `tabRelated Contract`

## Next Steps & Future Enhancements

### Immediate Next Steps (To Be Implemented)

1. **Standard Reports**
   - Contract Register
   - Expiring Contracts Report
   - Contract Value Analysis
   - Obligation Tracking Report
   - Payment Schedule Report
   - Compliance Report

2. **Dashboard Configuration**
   - Contract Overview widgets
   - Status distribution charts
   - Financial summary
   - Upcoming actions list

3. **Workflow Integration**
   - Create Frappe Workflows for approval process
   - Multi-level approval based on contract value
   - Email notifications at each workflow stage

4. **Custom Buttons**
   - "Create Amendment" button
   - "Renew Now" button
   - "Terminate" button
   - "Put On Hold" / "Resume" buttons

5. **Print Formats**
   - Professional contract print format
   - Amendment print format
   - Payment schedule print format

### Future Enhancements (Phase 2)

1. **AI-Powered Features**
   - Contract clause extraction from PDFs
   - Risk analysis using AI
   - Automated contract comparison

2. **Advanced Analytics**
   - Contract portfolio analysis
   - Vendor performance scoring
   - Cost-saving opportunity identification
   - Predictive analytics for renewals

3. **E-Signature Integration**
   - DocuSign integration
   - Adobe Sign integration
   - Digital signature support

4. **Mobile App**
   - Mobile contract viewing
   - Approval from mobile
   - Notifications

5. **Advanced Workflow**
   - Parallel approval paths
   - Conditional routing
   - Escalation rules
   - SLA tracking

6. **OCR Integration**
   - Scan paper contracts
   - Extract key information
   - Auto-populate fields

7. **Blockchain Integration**
   - Contract verification
   - Immutable audit trail
   - Smart contract support

8. **API Integrations**
   - Accounting system integration
   - CRM integration
   - Procurement system integration

9. **Advanced Reporting**
   - Custom report builder
   - Scheduled report delivery
   - Report dashboards
   - Data export to BI tools

## Technical Architecture

### Framework
- **Frappe Framework** (v14+)
- **Python 3.x**
- **MariaDB/MySQL**

### Design Patterns
- **MVC Pattern**: Model-View-Controller separation
- **Observer Pattern**: Event-driven notifications
- **Strategy Pattern**: Different renewal strategies
- **Factory Pattern**: Contract creation from templates

### Code Organization
```
contracts/
├── contracts/
│   ├── __init__.py
│   ├── hooks.py (app configuration & scheduled tasks)
│   ├── modules.txt
│   ├── patches.txt
│   ├── config/
│   │   ├── __init__.py
│   │   └── desktop.py (module configuration)
│   ├── contracts/
│   │   ├── __init__.py
│   │   └── doctype/
│   │       ├── contract/
│   │       │   ├── contract.json (field definitions)
│   │       │   ├── contract.py (business logic)
│   │       │   └── test_contract.py
│   │       ├── contract_type/
│   │       ├── contract_template/
│   │       └── [13 child table doctypes]/
│   └── templates/
├── setup.py
├── requirements.txt
├── license.txt
└── README.md
```

### Performance Considerations
- **Indexes**: Created on frequently queried fields (status, dates, party)
- **Caching**: Version history cached to reduce DB queries
- **Batch Processing**: Scheduled tasks process contracts in batches
- **Pagination**: List views paginated for large datasets

### Security
- **Role-Based Access Control**: Four distinct roles
- **Field-Level Permissions**: Internal notes hidden from parties
- **Audit Trail**: Track changes enabled on all sensitive fields
- **Document-Level Security**: Users see only their assigned contracts

## Troubleshooting

### Scheduled Tasks Not Running

```bash
# Check if scheduler is enabled
bench --site your-site-name console

>>> frappe.utils.scheduler.is_scheduler_inactive()
False  # Should be False

# Enable if inactive
>>> frappe.db.set_single_value("System Settings", "enable_scheduler", 1)

# Check scheduled job logs
bench --site your-site-name schedule ls
```

### Permissions Issues

```bash
# Reset permissions
bench --site your-site-name set-admin-password your-password
bench --site your-site-name add-to-hosts
```

### Migration Issues

```bash
# Run migrations
bench --site your-site-name migrate

# If migrations fail, check logs
bench --site your-site-name console

>>> frappe.reload_doctype("Contract")
```

## Support & Documentation

- **Frappe Documentation**: https://frappeframework.com/docs
- **ERPNext Documentation**: https://docs.erpnext.com
- **Frappe Forum**: https://discuss.frappe.io

## License

MIT License - See license.txt for details

## Credits

Built on the Frappe Framework
Designed for comprehensive contract lifecycle management
Follows ERPNext best practices and conventions

---

**Implementation Date**: November 2025
**Version**: 1.0.0
**Status**: Core Features Implemented ✅
