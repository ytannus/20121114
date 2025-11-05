# Frappe Contracts App - Data Model Documentation

## Overview

This document describes the data model for the Frappe Contracts application, including entity relationships, field definitions, and database schema considerations.

## Entity Relationship Diagram

```
┌─────────────────────┐
│   Contract Type     │
└──────────┬──────────┘
           │ 1:N
           │
┌──────────▼──────────┐         ┌─────────────────────┐
│     Contract        │◄────────│  Contract Template  │
│    (Main Entity)    │  N:1    └─────────────────────┘
└──────────┬──────────┘
           │
           │ Has many (1:N)
           ├─────────────► Contract Attachment
           ├─────────────► Contract Additional Party
           ├─────────────► Contract Payment Schedule
           ├─────────────► Contract Deliverable
           ├─────────────► Contract Obligation
           ├─────────────► Contract Compliance
           ├─────────────► Contract Milestone
           ├─────────────► Contract Amendment
           ├─────────────► Contract Version
           ├─────────────► Contract Review
           ├─────────────► Contract Performance Metric
           ├─────────────► Contract Regulatory Approval
           └─────────────► Related Contract

           │ Links to (N:1)
           ├─────────────► Customer/Supplier/Employee (Dynamic)
           ├─────────────► Department
           ├─────────────► Cost Center
           ├─────────────► Project
           ├─────────────► Currency
           ├─────────────► Address
           └─────────────► Contact
```

## Core Entities

### 1. Contract

**Entity Type**: Master Document
**Naming**: Auto-numbered (CONTRACT-.YYYY.-.####)
**Submittable**: Yes
**Amendable**: Yes
**Track Changes**: Yes

**Relationships**:
- Many-to-One: Contract Type
- Many-to-One: Party (Dynamic Link)
- Many-to-One: Department
- Many-to-One: Cost Center
- Many-to-One: Project
- Many-to-One: Currency
- Many-to-One: Parent Contract (Self-referencing)
- One-to-Many: All child tables

**Indexes**:
- Primary: name
- Secondary:
  - contract_type
  - status
  - party_type, party
  - start_date, end_date
  - department
  - cost_center
  - assigned_to

**Full-Text Search Fields**:
- contract_name
- description
- contract_terms
- scope_of_work

### 2. Contract Type

**Entity Type**: Master Document
**Naming**: Based on contract_type_name

**Purpose**: Define categories of contracts with default settings

**Relationships**:
- One-to-Many: Contract
- Many-to-One: Workflow

**Indexes**:
- Primary: name
- is_active

### 3. Contract Template

**Entity Type**: Master Document
**Naming**: Based on template_name

**Purpose**: Provide reusable contract templates

**Relationships**:
- Many-to-One: Contract Type
- Many-to-One: Currency
- Many-to-One: Payment Terms Template

**Indexes**:
- Primary: name
- contract_type
- is_active

## Child Table Entities

### 1. Contract Attachment

**Parent**: Contract
**Purpose**: Store multiple documents per contract

**Key Fields**:
- document_name (Index)
- document_type (Index)
- is_latest (Index)
- version

**Business Logic**:
- Auto-increment version for same document_name
- Only one document can have is_latest = 1 per document_name

### 2. Contract Additional Party

**Parent**: Contract
**Purpose**: Support multi-party contracts

**Key Fields**:
- party_type, party (Dynamic Link Index)
- role (Index)
- signature_status (Index)

**Business Logic**:
- Fetch party_name from linked party
- Track signature status independently for each party

### 3. Contract Payment Schedule

**Parent**: Contract
**Purpose**: Define payment milestones

**Key Fields**:
- due_date (Index)
- payment_status (Index)
- invoice_reference (Link Index)

**Business Logic**:
- Sum of all payment amounts should equal contract_value
- Auto-calculate percentage_of_total
- Auto-update payment_status when invoice is paid
- Mark as Overdue if due_date < today and status = Pending

**Aggregation**:
- Total Paid Amount = SUM(amount WHERE payment_status = 'Paid')
- Total Pending Amount = SUM(amount WHERE payment_status = 'Pending')
- Total Overdue Amount = SUM(amount WHERE payment_status = 'Overdue')

### 4. Contract Deliverable

**Parent**: Contract
**Purpose**: Track contract deliverables

**Key Fields**:
- due_date (Index)
- status (Index)
- assigned_to (Index)
- responsible_party (Index)

**Business Logic**:
- Send reminder notifications before due_date
- Mark as Delayed if due_date < today and status != Completed
- Track completion_percentage

**Aggregation**:
- Overall Completion = AVG(completion_percentage)
- Completed Count = COUNT(WHERE status = 'Completed')
- Delayed Count = COUNT(WHERE status = 'Delayed')

### 5. Contract Obligation

**Parent**: Contract
**Purpose**: Track obligations for both parties

**Key Fields**:
- obligated_party (Index)
- obligation_type (Index)
- due_date (Index)
- status (Index)
- frequency (Index)

**Business Logic**:
- For recurring obligations (frequency != One-time), auto-create next occurrence when completed
- Send reminders before due_date based on reminder_days_before
- Auto-update status to Overdue if due_date < today and status = Pending

**Recurring Logic**:
- If frequency = Monthly, create next obligation with due_date + 1 month
- If frequency = Quarterly, create next obligation with due_date + 3 months
- Continue until contract end_date

### 6. Contract Compliance

**Parent**: Contract
**Purpose**: Track compliance requirements

**Key Fields**:
- due_date (Index)
- status (Index)
- regulatory_body (Index)

**Business Logic**:
- Require evidence_document when status = Compliant
- Send alerts for Non-Compliant status
- Track verification by authorized user

### 7. Contract Milestone

**Parent**: Contract
**Purpose**: Track major milestones

**Key Fields**:
- target_date (Index)
- status (Index)
- payment_linked (Index)
- achieved (Index)

**Business Logic**:
- If payment_linked = true, block payment until achieved = true
- Calculate variance between target_date and actual_date
- Send notifications before target_date

**Aggregation**:
- Milestone Achievement Rate = COUNT(achieved = true) / COUNT(*)
- Average Delay = AVG(actual_date - target_date WHERE actual_date > target_date)

### 8. Contract Amendment

**Parent**: Contract
**Purpose**: Track all amendments

**Key Fields**:
- amendment_number (Unique per contract)
- amendment_date (Index)
- amendment_type (Index)
- effective_from (Index)

**Business Logic**:
- Auto-increment amendment_number
- Require approval_date before amendment becomes effective
- Create new contract version when amendment is approved
- Track before/after values for audit

### 9. Contract Version

**Parent**: Contract
**Purpose**: Maintain complete version history

**Key Fields**:
- version_number (Sequential)
- version_date (Index)
- changed_by (Index)

**Business Logic**:
- Auto-create version record on every save
- Store complete JSON snapshot of contract state
- Allow rollback to previous version (System Manager only)

**Storage**:
- Use compressed JSON for document_snapshot
- Archive old versions after 7 years

### 10. Contract Review

**Parent**: Contract
**Purpose**: Track periodic reviews

**Key Fields**:
- review_date (Index)
- reviewed_by (Index)
- review_type (Index)
- status (Index)

**Business Logic**:
- Auto-create next review based on review_frequency
- Send notification to reviewer before review_date
- Track action items separately

### 11. Contract Performance Metric

**Parent**: Contract
**Purpose**: Track KPIs

**Key Fields**:
- metric_name (Index)
- measurement_date (Index)
- status (Index)

**Business Logic**:
- Auto-calculate status based on actual_value vs target_value
- Support different calculation methods (higher is better, lower is better)
- Trend analysis over time

### 12. Contract Regulatory Approval

**Parent**: Contract
**Purpose**: Track regulatory approvals

**Key Fields**:
- regulatory_body (Index)
- status (Index)
- expiry_date (Index)

**Business Logic**:
- Send alerts before expiry_date
- Block contract activation if required approvals are not Approved
- Auto-update status to Expired when expiry_date < today

### 13. Related Contract

**Parent**: Contract
**Purpose**: Link related contracts

**Key Fields**:
- contract (Link Index)
- relationship_type (Index)

**Business Logic**:
- Prevent circular references
- Display related contracts in Contract view
- Auto-create reverse relationship (optional)

## Field Types and Constraints

### Data Types

| Field Type | Database Type | Max Length | Notes |
|------------|---------------|------------|-------|
| Data | VARCHAR | 140 | Standard text field |
| Small Text | TEXT | 65,535 | Multi-line text |
| Text | LONGTEXT | 4GB | Large text content |
| Text Editor | LONGTEXT | 4GB | Rich text with HTML |
| Int | INT | - | Integer numbers |
| Float | DECIMAL | (18,6) | Decimal numbers |
| Currency | DECIMAL | (18,6) | Monetary values |
| Percent | DECIMAL | (18,6) | Percentage values |
| Date | DATE | - | Date only |
| DateTime | DATETIME | - | Date and time |
| Check | TINYINT | - | Boolean (0/1) |
| Select | VARCHAR | 140 | Predefined options |
| Link | VARCHAR | 140 | Foreign key reference |
| Dynamic Link | VARCHAR | 140 | Dynamic foreign key |
| Attach | TEXT | - | File path |
| Table | - | - | Child table reference |

### Mandatory Fields

**Contract**:
- contract_name
- naming_series
- contract_type
- status
- party_type
- party
- start_date
- end_date

**Child Tables**:
- Each child table has required fields marked in specification

### Default Values

- status: "Draft"
- currency: System default currency
- notification_days: 30
- priority: "Medium"
- risk_level: "Low"
- requires_approval: Based on contract_type
- auto_renew: 0 (False)
- document_version: "1.0"
- renewal_count: 0

### Unique Constraints

- Contract: name (auto-generated)
- Contract Type: contract_type_name
- Contract Template: template_name
- Amendment: (parent, amendment_number) composite

### Check Constraints

- contract_value >= 0
- end_date > start_date
- notification_days >= 0
- renewal_count <= max_renewals
- completion_percentage >= 0 AND <= 100
- advance_payment_percentage >= 0 AND <= 100

## Calculated Fields

### Contract Level

1. **duration_days**
   ```python
   duration_days = (end_date - start_date).days
   ```

2. **contract_value_in_company_currency**
   ```python
   contract_value_in_company_currency = contract_value * exchange_rate
   ```

3. **days_to_expiry**
   ```python
   days_to_expiry = (end_date - today).days if status == 'Active' else None
   ```

4. **completion_percentage**
   ```python
   completion_percentage = (completed_deliverables / total_deliverables) * 100
   ```

5. **payment_received_percentage**
   ```python
   payment_received_percentage = (sum(paid_amounts) / contract_value) * 100
   ```

### Aggregated Fields

1. **total_paid_amount**
   ```python
   total_paid_amount = sum([row.amount for row in payment_schedule if row.payment_status == 'Paid'])
   ```

2. **total_pending_amount**
   ```python
   total_pending_amount = sum([row.amount for row in payment_schedule if row.payment_status == 'Pending'])
   ```

3. **deliverables_completion_rate**
   ```python
   deliverables_completion_rate = (count_completed / count_total) * 100
   ```

4. **obligations_completion_rate**
   ```python
   obligations_completion_rate = (count_completed / count_total) * 100
   ```

5. **average_performance_score**
   ```python
   average_performance_score = avg([metric.actual_value/metric.target_value for metric in metrics])
   ```

## Data Access Patterns

### Common Queries

1. **Get Active Contracts**
   ```sql
   SELECT * FROM `tabContract`
   WHERE status = 'Active'
   ORDER BY end_date ASC
   ```

2. **Get Expiring Contracts**
   ```sql
   SELECT * FROM `tabContract`
   WHERE status = 'Active'
   AND end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 90 DAY)
   ORDER BY end_date ASC
   ```

3. **Get Contracts by Party**
   ```sql
   SELECT * FROM `tabContract`
   WHERE party_type = 'Customer'
   AND party = 'CUST-00001'
   ORDER BY start_date DESC
   ```

4. **Get Overdue Obligations**
   ```sql
   SELECT c.name, o.obligation_name, o.due_date
   FROM `tabContract` c
   INNER JOIN `tabContract Obligation` o ON o.parent = c.name
   WHERE c.status = 'Active'
   AND o.status = 'Pending'
   AND o.due_date < CURDATE()
   ```

5. **Get Contract Value by Type**
   ```sql
   SELECT contract_type, SUM(contract_value) as total_value
   FROM `tabContract`
   WHERE status IN ('Active', 'Approved')
   GROUP BY contract_type
   ```

### Indexing Strategy

**Primary Indexes**:
- All tables have primary index on `name` field

**Foreign Key Indexes**:
- contract_type
- party_type, party
- department
- cost_center
- project
- currency
- assigned_to

**Query Optimization Indexes**:
- Composite index on (status, end_date) for expiring contracts
- Composite index on (party_type, party, status) for party contracts
- Index on start_date, end_date for date range queries

**Full-Text Indexes**:
- contract_name
- description
- contract_terms

## Data Integrity Rules

### Referential Integrity

1. Cannot delete Contract Type if contracts exist
2. Cannot delete Party if linked to contracts
3. Cannot delete User if assigned to contracts
4. Cannot delete Contract with:
   - Active status
   - Linked invoices
   - Related contracts

### Business Rule Constraints

1. Contract cannot be activated without approval
2. Active contract cannot be edited (amendments only)
3. End date cannot be before start date
4. Payment schedule total must equal contract value
5. Amendment requires new version
6. Cannot exceed max_renewals

### Cascade Rules

1. Delete Contract → Delete all child tables
2. Delete Contract Attachment → Delete physical file
3. Update Party → Update party_name in Contract
4. Update Contract Status → Trigger status change events

## Data Migration Considerations

### Import Template Structure

**Contract Import**:
- CSV template with all mandatory fields
- Support for bulk import via Data Import tool
- Validation before import
- Error logging and reporting

**Child Table Import**:
- Separate CSV for each child table
- Link via parent contract name
- Sequential import (parent first, then children)

### Data Validation During Import

1. Date format validation
2. Party existence check
3. Contract Type validation
4. Numeric value validation
5. Duplicate detection
6. Business rule validation

## Archival Strategy

### Archive Criteria

- Contracts with status = 'Expired' or 'Terminated'
- End date > 7 years ago
- No pending obligations
- All invoices settled

### Archive Process

1. Mark contract as archived
2. Move attachments to archive storage
3. Keep metadata in database
4. Create archive reference
5. Remove from active searches

### Retention Policy

- Active contracts: Indefinite
- Expired contracts: 7 years
- Archived contracts: 10 years
- Audit logs: 10 years
- Deleted contracts: Soft delete for 1 year

## Performance Optimization

### Caching Strategy

1. Cache Contract Types (rarely change)
2. Cache Contract Templates (rarely change)
3. Cache active contracts for dashboard
4. Invalidate cache on update

### Query Optimization

1. Use appropriate indexes
2. Limit result sets with pagination
3. Use Redis for frequently accessed data
4. Avoid N+1 queries for child tables
5. Use aggregate queries for reports

### Database Partitioning

Consider partitioning `tabContract` by year for large installations:
- Partition by YEAR(creation_date)
- Separate partitions for each fiscal year
- Archive old partitions

## Backup and Recovery

### Backup Strategy

1. **Daily Backups**:
   - Full database backup
   - File attachments backup
   - Store for 30 days

2. **Weekly Backups**:
   - Full backup
   - Store for 1 year

3. **Monthly Backups**:
   - Full backup
   - Store for 7 years

### Recovery Procedures

1. **Point-in-Time Recovery**:
   - Restore from daily backup
   - Apply transaction logs

2. **Selective Recovery**:
   - Restore specific contract
   - Use version history

3. **Disaster Recovery**:
   - Restore from offsite backup
   - RPO: 24 hours
   - RTO: 4 hours

## Data Security

### Encryption

1. **At Rest**:
   - Encrypt sensitive fields (financial data)
   - Encrypt file attachments

2. **In Transit**:
   - HTTPS for all communications
   - Encrypted database connections

### Access Control

1. Row-level security based on permissions
2. Field-level access control
3. Department-based access
4. User-based access

### Audit Logging

1. Log all data changes
2. Track user actions
3. Store logs for 10 years
4. Tamper-proof audit trail

## Data Quality

### Validation Rules

1. Mandatory field validation
2. Format validation (dates, numbers)
3. Range validation
4. Business rule validation
5. Cross-field validation

### Data Cleansing

1. Remove duplicate contracts
2. Standardize party names
3. Clean up orphaned records
4. Fix invalid dates
5. Normalize currency values

### Data Quality Metrics

1. Completeness: % of required fields filled
2. Accuracy: % of valid data
3. Consistency: % of cross-field valid data
4. Timeliness: % of up-to-date records
5. Uniqueness: % of duplicate-free records

Target: >95% for all metrics
