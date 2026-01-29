# ICS Etimad Tenders CRM & Tender Management Integration Guide

## Overview

This guide explains how the **ics_etimad_tenders_crm** (web scraper) and **ics_tender_management** (lifecycle management) modules work together to provide a complete tender management solution for Saudi Arabian businesses.

---

## Module Architecture

### Module 1: ics_etimad_tenders_crm (Data Acquisition)
**Purpose**: Scrapes and stores tenders from Etimad portal
**Main Model**: `ics.etimad.tender`

**Key Features**:
- Automated web scraping from portal.etimad.sa
- Daily synchronization (scheduled cron job)
- Anti-bot protection handling
- Deadline tracking with urgency alerts
- One-click CRM opportunity creation

### Module 2: ics_tender_management (Lifecycle Management)
**Purpose**: Manages complete tender lifecycle from technical study to execution
**Main Model**: `ics.tender`

**Key Features**:
- BoQ management
- Vendor RFQ via Purchase Agreements
- Vendor comparison and selection
- Automated quotation generation
- Project creation from won tenders

---

## Integration Flow

### Phase 1: Tender Discovery & Lead Creation

```
Etimad Portal (portal.etimad.sa)
    ↓ (Automatic Scraping)
ics.etimad.tender (Scraped Tender)
    ↓ (User Action: Create Opportunity)
crm.lead (CRM Opportunity)
    ↓ (User Action: Create Tender)
ics.tender (Tender Management)
```

#### Step 1: Automatic Tender Scraping

```python
# Scheduled daily at 6 AM
# Model: ics.etimad.tender
# Method: action_fetch_tenders_cron()

# Fetches tenders from Etimad API
# Creates/updates ics.etimad.tender records
```

**Fields Captured from Etimad**:
- `tender_id_string` → Unique Etimad identifier
- `reference_number` → Official reference
- `tender_number` → Tender number
- `name` → Tender title
- `agency_name` → Government agency
- `tender_type` → Type (supply, services, etc.)
- `activity_name` → Activity category
- `offers_deadline` → Submission deadline
- `last_enquiry_date` → Last date for questions
- `invitation_cost` → Document purchase cost
- `financial_fees` → Financial fees

#### Step 2: View Scraped Tenders

Navigate to: **Etimad Tenders > Tenders**

Features:
- List/Kanban view of all scraped tenders
- Color-coded by urgency (red = ≤3 days, yellow = ≤7 days)
- Filters: favorites, status, agency, activity
- Direct link to Etimad portal
- Remaining days calculation

#### Step 3: Create CRM Opportunity

From `ics.etimad.tender` form view:

```xml
<button name="action_create_opportunity"
        string="Create Opportunity"
        type="object"/>
```

This creates a `crm.lead` with:
- Name from tender title
- Partner name from agency
- Expected revenue from total fees
- Deadline from offers deadline
- Priority based on urgency
- Link back to `etimad_tender_id`

#### Step 4: Create Tender Management Record

From `crm.lead` form view:

```xml
<button name="action_create_tender"
        string="Create Tender"
        type="object"/>
```

This creates `ics.tender` with auto-populated fields from:
- CRM opportunity data
- Linked Etimad tender data (if exists)

**Auto-populated Fields**:
```python
@api.onchange('etimad_tender_id')
def _onchange_etimad_tender_id(self):
    if self.etimad_tender_id:
        self.tender_number = self.etimad_tender_id.tender_number
        self.tender_title = self.etimad_tender_id.tender_title
        self.announcement_date = self.etimad_tender_id.announcement_date
        self.submission_deadline = self.etimad_tender_id.submission_deadline
```

---

### Phase 2: Technical & Financial Study

#### BoQ Management

**Model**: `ics.tender.boq.line`

1. **Add BoQ Lines** to tender:
   ```
   Tender Form → BoQ Tab → Add Line
   ```

2. **Fields per Line**:
   - Product (from product catalog)
   - Description
   - Quantity & UoM
   - Estimated Cost
   - Technical Specifications (HTML)
   - Notes

3. **Auto-calculation**:
   - Unit Price = Estimated Cost / Quantity
   - Total Estimated Cost = Sum of all lines

#### Vendor RFQ Process

**Model**: `purchase.requisition` (Purchase Agreement)

1. **Create Purchase Agreement**:
   ```
   Tender Form → Button: "Create RFQ (Purchase Agreement)"
   ```

2. **System Actions**:
   ```python
   def action_create_purchase_agreement(self):
       # Creates purchase.requisition
       # Copies all BoQ lines to requisition lines
       # Links requisition to tender via tender_id field
   ```

3. **Send to Vendors**:
   - Purchase Agreement → Send by Email
   - Vendors submit quotations
   - System tracks vendor responses

4. **Vendor Offers** (`ics.tender.vendor.offer`):
   - Manually add vendor offers to each BoQ line
   - Or import from Purchase Order quotes
   - Fields: vendor_id, unit_price, delivery_lead_time, payment_terms

#### Vendor Comparison

**Wizard**: `ics.tender.vendor.comparison.wizard`

1. **Open Comparison**:
   ```
   Tender Form → Button: "Compare Vendors"
   ```

2. **Wizard Features**:
   - Shows all BoQ lines
   - Displays best offer per line (lowest unit price)
   - Calculates savings vs. estimated costs
   - Shows savings percentage
   - Displays number of offers per line
   - Link to view all offers

3. **Selection Process**:
   ```python
   def action_apply_selection(self):
       # For each line, sets:
       # boq_line.selected_vendor_id = best_vendor
       # boq_line.selected_vendor_price = best_total
   ```

---

### Phase 3: Quotation Generation

**Wizard**: `ics.tender.quotation.wizard`

#### Configuration Options

```xml
<field name="margin_percentage"/>  <!-- Default: 20% -->
<field name="use_vendor_costs"/>   <!-- vs estimated costs -->
<field name="pricelist_id"/>       <!-- Sales pricelist -->
<field name="payment_term_id"/>    <!-- Payment terms -->
<field name="validity_date"/>      <!-- Quotation validity -->
<field name="notes"/>              <!-- Terms & conditions -->
```

#### Preview & Calculation

For each BoQ line:
```python
cost = selected_vendor_price if use_vendor_costs else estimated_cost
margin = cost * (margin_percentage / 100)
unit_price = (cost + margin) / quantity
total = cost + margin
```

#### Generate Sales Order

**Model**: `sale.order`

```python
def action_generate_quotation(self):
    # Creates sale.order with:
    # - tender_id link
    # - All BoQ lines as order lines
    # - Calculated prices with margin
    # - Payment terms and validity

    # Updates tender:
    # - state = 'quotation'
    # - margin_percentage saved
```

---

### Phase 4: Submission & Evaluation

#### Submission Workflow

```
State: quotation → submitted → evaluation → won/lost
```

**Actions**:
1. `action_submit_tender()`: Marks as submitted
2. `action_mark_won()`:
   - Sets state = 'won'
   - Syncs with CRM opportunity (marks won)
   - Enables project creation
3. `action_mark_lost()`:
   - Sets state = 'lost'
   - Captures lost reason

---

### Phase 5: Project Execution

**Wizard**: `ics.tender.project.wizard`

#### One-Click Project Creation

```
Tender Form (state=won) → Button: "Create Project"
```

**Wizard Options**:
- Project name (auto-filled)
- Project manager
- Link to sales order
- Create tasks from BoQ (checkbox)
- Start date

**System Creates**:

```python
# project.project record
{
    'name': wizard.name,
    'partner_id': tender.partner_id,
    'tender_id': tender.id,
    'sale_order_id': wizard.sale_order_id,
    'user_id': wizard.user_id,
}

# project.task records (if create_from_boq = True)
for boq_line in tender.boq_line_ids:
    {
        'name': boq_line.name,
        'project_id': project.id,
        'description': boq_line.specifications,
    }
```

---

## Field Relationships & Data Flow

### Key Foreign Keys

```python
# ics.etimad.tender
opportunity_id → crm.lead  # Linked opportunity

# crm.lead
etimad_tender_id → ics.etimad.tender  # Source tender
tender_ids → ics.tender[]  # Management tenders

# ics.tender
etimad_tender_id → ics.etimad.tender  # Source data
lead_id → crm.lead  # Opportunity
requisition_ids → purchase.requisition[]  # RFQs
quotation_ids → sale.order[]  # Quotations
project_ids → project.project[]  # Projects

# ics.tender.boq.line
tender_id → ics.tender
product_id → product.product
vendor_offer_ids → ics.tender.vendor.offer[]
selected_vendor_id → res.partner

# ics.tender.vendor.offer
boq_line_id → ics.tender.boq.line
vendor_id → res.partner
purchase_order_id → purchase.order

# purchase.requisition
tender_id → ics.tender

# sale.order
tender_id → ics.tender

# project.project
tender_id → ics.tender
sale_order_id → sale.order
```

---

## Smart Buttons & Navigation

### From ics.etimad.tender (Scraped Tender)

- **Create Opportunity** → Creates `crm.lead`
- **View Opportunity** → Opens linked opportunity
- **Open URL** → Opens tender on Etimad portal
- **Toggle Favorite** → Marks for quick access

### From crm.lead (Opportunity)

- **Tenders** (stat button) → Lists all `ics.tender` records
- **Create Tender** → Creates new `ics.tender`

### From ics.tender (Tender Management)

- **BoQ Lines** (stat button) → Opens BoQ lines
- **RFQs** (stat button) → Opens Purchase Agreements
- **Quotations** (stat button) → Opens Sales Orders
- **Projects** (stat button) → Opens Projects
- **Documents** (stat button) → Opens Attachments

### From purchase.requisition (RFQ)

- **View Tender** (stat button) → Opens `ics.tender`

### From sale.order (Quotation)

- **View Tender** (stat button) → Opens `ics.tender`

### From project.project (Project)

- **View Tender** (stat button) → Opens `ics.tender`
- **View Sale Order** (stat button) → Opens `sale.order`

---

## Configuration & Settings

### Etimad Scraper Settings

**Location**: Settings → Etimad Tenders CRM

```python
# Auto Sync
etimad_auto_sync = Boolean (Default: True)
etimad_sync_interval = Integer (Default: 24 hours)
etimad_fetch_page_size = Integer (Default: 50)

# Auto Create Opportunities
etimad_auto_create_opportunity = Boolean (Default: False)
etimad_min_tender_value = Float (Default: 10000 SAR)

# Notifications
etimad_notify_new_tenders = Boolean (Default: True)
etimad_notify_urgent_deadlines = Boolean (Default: True)

# Archive
etimad_auto_archive = Boolean (Default: False)
etimad_archive_days = Integer (Default: 90)
```

### Tender Management Settings

**Location**: Tender Management → Configuration → Tender Stages

Customize workflow stages:
- Add/remove stages
- Set sequence and fold status
- Mark won/lost stages
- Add stage requirements

---

## Reports

### Available Reports

1. **Tender Report** (`ics.tender`)
   - Complete tender information
   - Financial summary
   - Status and dates

2. **Tender BoQ Report** (`ics.tender`)
   - Detailed BoQ with line items
   - Quantities, unit prices, totals
   - Grand total calculation

---

## Security & Access Control

### User Groups

**ics_etimad_tenders_crm**:
- No specific groups (uses base CRM groups)

**ics_tender_management**:
- `group_tender_user`: Can manage own tenders
- `group_tender_manager`: Full access to all tenders

### Record Rules

**Tender User Rule**:
```python
[
    '|',
    ('user_id', '=', user.id),  # Own tenders
    ('user_id', '=', False)      # Unassigned
]
```

**Tender Manager Rule**:
```python
[(1, '=', 1)]  # All records
```

---

## Best Practices

### 1. Daily Workflow

**Morning (6 AM - Automatic)**:
- System scrapes new tenders from Etimad
- New records created in `ics.etimad.tender`

**Morning Review**:
1. Check **Etimad Tenders > Tenders**
2. Filter by urgent (deadline ≤ 7 days)
3. Review new tenders
4. Mark interesting ones as favorites

**Opportunity Creation**:
1. For each relevant tender → **Create Opportunity**
2. Add contact person if known
3. Assign to sales team
4. Set probability

**Tender Management**:
1. From opportunity → **Create Tender**
2. Review auto-populated data
3. Add any additional details

### 2. Technical Study Phase

1. Upload and review tender documents (attachments)
2. Analyze technical requirements
3. Create BoQ lines:
   - Add products from catalog
   - Set quantities accurately
   - Add technical specifications
   - Include estimated costs

### 3. Financial Study Phase

1. Click **Create RFQ (Purchase Agreement)**
2. Review generated RFQ
3. Add vendors to agreement
4. Send RFQs via email
5. Wait for vendor responses
6. Enter vendor offers on each BoQ line
7. Use **Compare Vendors** wizard
8. Review savings and select best vendors

### 4. Quotation Phase

1. Click **Prepare Quotation**
2. Click **Generate Sales Quotation**
3. Configure margin (20% default)
4. Choose cost source (vendor/estimated)
5. Set payment terms
6. Review preview
7. Generate quotation
8. Review and send to customer

### 5. Submission Phase

1. Click **Submit Tender**
2. Upload submission documents
3. Schedule follow-up activities
4. Move to **Under Evaluation** stage

### 6. Won Phase

1. Click **Mark as Won**
2. Enter winning reason
3. Record actual revenue
4. Click **Create Project**
5. Configure project settings
6. Enable task creation from BoQ
7. Assign project manager

---

## Troubleshooting

### Etimad Scraper Issues

**Problem**: "Etimad portal is blocking requests"
**Solution**:
- Wait 1-2 hours before retry
- Reduce fetch page size
- Check internet connectivity

**Problem**: "No data in response"
**Solution**:
- Etimad portal may be down
- Check https://portal.etimad.sa manually
- Try again later

### Integration Issues

**Problem**: Cannot create tender from opportunity
**Solution**:
- Ensure `ics_etimad_tenders_crm` is installed
- Check opportunity has partner set
- Verify user has tender user rights

**Problem**: etimad_tender_id field not showing
**Solution**:
- Update module list
- Restart Odoo service
- Clear browser cache

### BoQ & Vendor Issues

**Problem**: Vendor offers not showing in comparison
**Solution**:
- Ensure offers are linked to correct BoQ line
- Check `boq_line_id` field is set
- Verify offers have unit_price set

**Problem**: Selected vendor price not calculating
**Solution**:
- Ensure vendor is selected on BoQ line
- Check vendor has an offer for that line
- Verify offer has total_price computed

---

## API Integration Examples

### Fetch Etimad Tenders Programmatically

```python
# Manual fetch
etimad_tender_obj = env['ics.etimad.tender']
etimad_tender_obj.fetch_etimad_tenders(
    page_size=20,
    page_number=1
)
```

### Create Tender from Python

```python
# From Etimad tender
etimad_tender = env['ics.etimad.tender'].browse(1)
opportunity = etimad_tender.action_create_opportunity()

# From Opportunity
lead = env['crm.lead'].browse(1)
tender_action = lead.action_create_tender()
```

### Generate Quotation Programmatically

```python
tender = env['ics.tender'].browse(1)

# Create wizard
wizard = env['ics.tender.quotation.wizard'].create({
    'tender_id': tender.id,
    'margin_percentage': 25.0,
    'use_vendor_costs': True,
})

# Generate
wizard.action_generate_quotation()
```

---

## Module Dependencies

### Required Modules

**ics_etimad_tenders_crm**:
- `base`
- `crm`
- `mail`
- `web`

**ics_tender_management**:
- `base`
- `crm`
- `sale_management`
- `purchase`
- `purchase_requisition`
- `project`
- `ics_etimad_tenders_crm`

### External Python Dependencies

```bash
pip install requests
```

---

## Support & Contact

**iCloud Solutions**

- **Website**: https://icloud-solutions.net
- **Email**: contact@icloud-solutions.net
- **WhatsApp**: +216 50 271 737

**Module Information**:
- **License**: ics_etimad_tenders_crm (LGPL-3), ics_tender_management (OPL-1)
- **Price**: ics_tender_management - €2,500
- **Version**: 18.0.1.0.0

---

## Conclusion

This integration provides a complete, automated tender management solution for Saudi businesses:

1. **Automatic Data Acquisition**: Etimad scraper eliminates manual tender searching
2. **Seamless CRM Integration**: Links tenders to sales pipeline
3. **Complete Lifecycle Management**: From BoQ to project execution
4. **Vendor Management**: Compare offers, select best vendors
5. **Automated Quotation**: Generate quotes with margin calculation
6. **Project Execution**: One-click project creation with tasks

**End Result**: Win more tenders, reduce manual work, improve efficiency!
