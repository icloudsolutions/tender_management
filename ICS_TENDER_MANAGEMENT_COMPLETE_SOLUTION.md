# ICS Tender Management - Complete Solution

## 🎯 Overview

A comprehensive **2-module solution** for Saudi Arabian businesses to manage government tenders from the Etimad portal through complete project execution.

---

## 📦 Module Package

### Module 1: ics_etimad_tenders_crm
**Purpose**: Automated Tender Data Acquisition
**License**: LGPL-3 (Free)
**Status**: ✅ Already Implemented

**Capabilities**:
- ✅ Scrapes tenders from portal.etimad.sa API
- ✅ Daily automated synchronization (scheduled cron)
- ✅ Anti-bot protection handling with retry mechanism
- ✅ Stores tender data in `ics.etimad.tender` model
- ✅ Creates CRM opportunities with one click
- ✅ Tracks deadlines with urgency indicators
- ✅ Hijri calendar date support
- ✅ Financial tracking (invitation costs, fees)

**Key Features**:
```python
# Auto-fetch from Etimad portal
@api.model
def fetch_etimad_tenders(self, page_size=20, page_number=1):
    # Fetches tenders from https://tenders.etimad.sa
    # Creates/updates ics.etimad.tender records
    # Returns notification with count
```

### Module 2: ics_tender_management
**Purpose**: Complete Tender Lifecycle Management
**License**: OPL-1 (Proprietary)
**Price**: €2,500
**Status**: ✅ Fully Created & Documented

**Capabilities**:
- ✅ Full tender lifecycle from registration to execution
- ✅ Bill of Quantities (BoQ) management
- ✅ Purchase Agreement (RFQ) integration
- ✅ Advanced vendor comparison wizard
- ✅ Automated sales quotation generation
- ✅ Margin calculation and pricing
- ✅ One-click project creation
- ✅ Task generation from BoQ lines
- ✅ Complete CRM, Purchase, Sales, Project integration

---

## 🔄 Complete Workflow

### Saudi Tender Management Process

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: LEAD CREATION & REGISTRATION                      │
└─────────────────────────────────────────────────────────────┘
    ↓
Etimad Portal (portal.etimad.sa)
    ↓ [Automatic Scraping - Daily at 6 AM]
ics.etimad.tender (Scraped Tender)
    ↓ [User: Create Opportunity]
crm.lead (CRM Opportunity)
    ↓ [User: Create Tender]
ics.tender (Tender Management)

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: TECHNICAL & FINANCIAL STUDY                        │
└─────────────────────────────────────────────────────────────┘
    ↓
Add BoQ Lines (ics.tender.boq.line)
    ├─ Products
    ├─ Quantities
    ├─ Estimated Costs
    └─ Technical Specifications
    ↓ [User: Create RFQ]
Purchase Agreement (purchase.requisition)
    ↓ [Send to Multiple Vendors]
Vendor Offers (ics.tender.vendor.offer)
    ↓ [User: Compare Vendors]
Vendor Comparison Wizard
    ↓ [User: Apply Best Vendors]
Selected Vendors on BoQ

┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: QUOTATION & SUBMISSION                            │
└─────────────────────────────────────────────────────────────┘
    ↓ [User: Generate Quotation]
Quotation Wizard
    ├─ Margin % (Default 20%)
    ├─ Cost Source (Vendor/Estimated)
    ├─ Payment Terms
    └─ Preview & Calculate
    ↓ [User: Generate]
Sales Order (sale.order)
    ↓ [User: Submit Tender]
Tender Submitted
    ↓ [Customer Evaluation]
Under Evaluation
    ↓ [User: Mark as Won/Lost]
Won or Lost

┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: EXECUTION (Won Tenders Only)                      │
└─────────────────────────────────────────────────────────────┘
    ↓ [User: Create Project]
Project Wizard
    ├─ Project Name
    ├─ Project Manager
    ├─ Link Sales Order
    └─ Create Tasks from BoQ
    ↓ [Generate]
Project (project.project)
    ├─ Customer Info
    ├─ Tender Link
    ├─ Sales Order Link
    └─ Tasks (from BoQ lines)
```

---

## 📊 Data Models & Relationships

### Core Models Created

#### 1. ics.tender (Main Model)
```python
_name = 'ics.tender'
_inherit = ['mail.thread', 'mail.activity.mixin']

# Key Fields:
- name: Auto-sequence (TND/00001)
- etimad_tender_id → ics.etimad.tender
- lead_id → crm.lead
- partner_id → res.partner
- tender_number, tender_title, tender_category
- submission_deadline, days_to_deadline, is_urgent
- boq_line_ids → ics.tender.boq.line[]
- requisition_ids → purchase.requisition[]
- quotation_ids → sale.order[]
- project_ids → project.project[]
- state: draft → technical → financial → quotation → submitted → won/lost
```

#### 2. ics.tender.stage (Kanban Stages)
```python
_name = 'ics.tender.stage'
_order = 'sequence'

# 9 Default Stages:
1. Draft
2. Technical Study
3. Financial Study
4. Quotation Prepared
5. Submitted
6. Under Evaluation
7. Won
8. Lost
9. Cancelled
```

#### 3. ics.tender.boq.line (Bill of Quantities)
```python
_name = 'ics.tender.boq.line'
_order = 'sequence'

# Key Fields:
- tender_id → ics.tender
- product_id → product.product
- name, specifications, quantity, uom_id
- estimated_cost, unit_price
- vendor_offer_ids → ics.tender.vendor.offer[]
- selected_vendor_id → res.partner
- selected_vendor_price
```

#### 4. ics.tender.vendor.offer
```python
_name = 'ics.tender.vendor.offer'
_order = 'total_price'

# Key Fields:
- boq_line_id → ics.tender.boq.line
- vendor_id → res.partner
- unit_price, total_price
- delivery_lead_time, payment_terms
- is_selected (computed)
```

### Integration Models (Extended)

#### crm.lead (Extended)
```python
_inherit = 'crm.lead'

# Added Fields:
- etimad_tender_id → ics.etimad.tender
- tender_ids → ics.tender[]
- tender_count (computed)

# New Actions:
- action_view_tenders()
- action_create_tender()
```

#### purchase.requisition (Extended)
```python
_inherit = 'purchase.requisition'

# Added Fields:
- tender_id → ics.tender

# New Actions:
- action_view_tender()
```

#### sale.order (Extended)
```python
_inherit = 'sale.order'

# Added Fields:
- tender_id → ics.tender

# New Actions:
- action_view_tender()
```

#### project.project (Extended)
```python
_inherit = 'project.project'

# Added Fields:
- tender_id → ics.tender
- sale_order_id → sale.order

# New Actions:
- action_view_tender()
- action_view_sale_order()
```

---

## 🧙 Wizards

### 1. Vendor Comparison Wizard
**Model**: `ics.tender.vendor.comparison.wizard`

**Purpose**: Compare all vendor offers side-by-side

**Features**:
- Displays best offer per BoQ line
- Calculates savings vs estimated costs
- Shows savings percentage
- Displays number of offers per line
- One-click application of best vendors
- Link to view all offers for each line

**Output**:
```python
# Updates each BoQ line:
boq_line.selected_vendor_id = best_vendor
boq_line.selected_vendor_price = best_total
```

### 2. Generate Quotation Wizard
**Model**: `ics.tender.quotation.wizard`

**Purpose**: Generate sales quotation with margin calculation

**Configuration**:
- Margin percentage (default 20%)
- Use vendor costs vs estimated costs
- Pricelist selection
- Payment terms
- Validity date
- Terms and conditions

**Preview**:
- Shows all lines with cost, margin, unit price, total
- Displays total cost, margin, and final amount

**Output**:
```python
# Creates sale.order with:
- All BoQ lines as order lines
- Calculated prices with margin
- Linked to tender
- Updates tender state to 'quotation'
```

### 3. Create Project Wizard
**Model**: `ics.tender.project.wizard`

**Purpose**: Create project from won tender

**Configuration**:
- Project name (auto-filled from tender)
- Project manager
- Link to sales order
- Create tasks from BoQ (checkbox)
- Start date

**Output**:
```python
# Creates project.project with:
- Customer and tender links
- Sales order integration
- Tasks generated from BoQ lines (optional)
```

---

## 🎨 User Interface

### Views Created

#### Tender Views
1. **Kanban View**: Visual workflow with stage columns
   - Color-coded cards (urgent, won, lost)
   - Priority indicators
   - Activity tracking
   - Smart buttons visible

2. **Tree View**: List of all tenders
   - Decoration rules (urgent = red, won = green)
   - Grouping by stage, team, category
   - Financial totals

3. **Form View**: Complete tender details
   - Status bar with clickable stages
   - Smart buttons (BoQ, RFQs, Quotations, Projects, Documents)
   - BoQ inline tree (editable)
   - Description, notes, specifications tabs
   - Win/loss details section

4. **Search View**: Advanced filtering
   - My Tenders, Urgent, High Priority
   - By state, stage, category
   - Date filters
   - Group by: partner, user, team, stage, category

#### BoQ Views
1. **Tree View**: Editable inline
   - Drag-drop sequencing
   - Sum totals
   - Vendor selection

2. **Form View**: Detailed line editing
   - Product and specifications
   - Vendor offers sub-list
   - Technical specs tab

#### Wizard Views
1. **Vendor Comparison**: Table with best offers and savings
2. **Quotation Generation**: Preview lines with margin calculation
3. **Project Creation**: Simple form with configuration options

---

## 🔐 Security

### Security Groups
```xml
<!-- Module Category -->
<record id="module_category_tender_management">
    <field name="name">Tender Management</field>
</record>

<!-- User Group -->
<record id="group_tender_user">
    <field name="name">User</field>
    <!-- Can manage own tenders -->
</record>

<!-- Manager Group -->
<record id="group_tender_manager">
    <field name="name">Manager</field>
    <!-- Full access to all tenders -->
</record>
```

### Access Rights (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ics_tender_user,ics.tender.user,model_ics_tender,group_tender_user,1,1,1,0
access_ics_tender_manager,ics.tender.manager,model_ics_tender,group_tender_manager,1,1,1,1
# ... (8 access rights total)
```

### Record Rules
```xml
<!-- User Rule: Own tenders only -->
<record id="tender_rule_user">
    <field name="domain_force">[
        '|',
        ('user_id', '=', user.id),
        ('user_id', '=', False)
    ]</field>
</record>

<!-- Manager Rule: All tenders -->
<record id="tender_rule_manager">
    <field name="domain_force">[(1, '=', 1)]</field>
</record>
```

---

## 📄 Reports

### 1. Tender Report (PDF)
**Template**: `report_tender_document`

**Content**:
- Tender header information
- Customer and dates
- Status and stage
- Description
- Financial summary table:
  - Total Estimated Cost
  - Total Vendor Cost
  - Margin (with percentage)
  - Total Quotation Amount

### 2. Tender BoQ Report (PDF)
**Template**: `report_tender_boq_document`

**Content**:
- Tender title and customer
- Date
- BoQ table:
  - Item number
  - Description with product code
  - Quantity and UoM
  - Unit price
  - Total per line
- Grand total

---

## 📁 Module Structure

```
ics_tender_management/
├── __init__.py
├── __manifest__.py
├── README.md
├── DOCUMENTATION.md (50+ pages)
├── INTEGRATION_GUIDE.md (Complete integration flow)
├── CHANGELOG.md
├── LICENSE (OPL-1)
├── COPYRIGHT
│
├── models/
│   ├── __init__.py
│   ├── tender_stage.py
│   ├── tender.py (400+ lines)
│   ├── tender_boq.py (Vendor offers included)
│   ├── crm_lead.py (CRM integration)
│   ├── purchase_requisition.py
│   ├── sale_order.py
│   └── project_project.py
│
├── views/
│   ├── tender_views.xml (Kanban, Tree, Form, Search)
│   ├── tender_boq_views.xml
│   ├── crm_lead_views.xml (Smart button + Create Tender)
│   ├── purchase_requisition_views.xml
│   ├── sale_order_views.xml
│   └── tender_menus.xml (Complete menu structure)
│
├── wizard/
│   ├── __init__.py
│   ├── vendor_comparison_wizard.py
│   ├── vendor_comparison_wizard_views.xml
│   ├── generate_quotation_wizard.py
│   ├── generate_quotation_wizard_views.xml
│   ├── create_project_wizard.py
│   └── create_project_wizard_views.xml
│
├── security/
│   ├── tender_security.xml (Groups + Record Rules)
│   └── ir.model.access.csv (8 access rights)
│
├── data/
│   ├── tender_sequence.xml (TND/00001)
│   └── tender_stage_data.xml (9 default stages)
│
├── report/
│   ├── tender_report.xml (2 PDF reports)
│   └── tender_templates.xml (QWeb templates)
│
└── static/
    ├── description/
    │   ├── icon.svg
    │   ├── index.html (Module description)
    │   └── BANNER_INFO.txt (Design specs)
    └── src/
        └── css/
            └── tender_kanban.css (Custom styling)
```

---

## 🚀 Installation & Setup

### Prerequisites
```bash
# Python dependencies
pip install requests

# Odoo modules
- crm
- sale_management
- purchase
- purchase_requisition
- project
- ics_etimad_tenders_crm (must be installed first)
```

### Installation Steps

1. **Install ics_etimad_tenders_crm**:
   ```
   Apps → Update Apps List → Search "Etimad" → Install
   ```

2. **Configure Etimad Scraper**:
   ```
   Settings → Etimad Tenders CRM
   - Enable Auto Sync: ✓
   - Sync Interval: 24 hours
   - Tenders per Sync: 50
   ```

3. **Test Etimad Scraping**:
   ```
   Etimad Tenders → Tenders → Button: "Sync Now"
   ```

4. **Install ics_tender_management**:
   ```
   Apps → Update Apps List → Search "ICS Tender" → Install
   ```

5. **Configure Tender Stages** (Optional):
   ```
   Tender Management → Configuration → Tender Stages
   - Review and customize if needed
   ```

6. **Assign User Rights**:
   ```
   Settings → Users & Companies → Users
   - Select user
   - Add to "Tender Management / User" or "Manager"
   ```

---

## 💡 Usage Examples

### Example 1: Complete Workflow

**Day 1 - Morning (Automatic)**:
```
06:00 - System scrapes Etimad portal
06:05 - 50 new tenders imported
```

**Day 1 - 09:00 (Manual)**:
```
User: Navigate to Etimad Tenders > Tenders
User: Filter by "Urgent" (deadline ≤ 7 days)
User: Find relevant tender for "School Furniture Supply"
User: Click "Create Opportunity"
System: Creates CRM opportunity
User: Assign to Sales Team, set probability 80%
```

**Day 1 - 10:00 (Manual)**:
```
User: Open CRM opportunity
User: Click "Create Tender"
System: Creates tender with auto-populated data
User: Review tender details
```

**Day 2 (Technical Study)**:
```
User: Open tender
User: State → "Start Technical Study"
User: Add BoQ lines:
  - 100x School Desk (Estimated: 500 SAR each)
  - 100x School Chair (Estimated: 200 SAR each)
  - Total Estimated: 70,000 SAR
```

**Day 3 (Financial Study)**:
```
User: Click "Create RFQ (Purchase Agreement)"
System: Creates Purchase Agreement with 2 lines
User: Add 3 vendors to agreement
User: Send RFQ emails
```

**Day 5 (Vendor Responses)**:
```
Vendor A: Desk 480 SAR, Chair 190 SAR
Vendor B: Desk 500 SAR, Chair 180 SAR
Vendor C: Desk 470 SAR, Chair 195 SAR

User: Enter offers in BoQ vendor offers
```

**Day 6 (Vendor Selection)**:
```
User: Click "Compare Vendors"
System: Shows best prices:
  - Desk: Vendor C (470 SAR) - Saving 30 SAR (6%)
  - Chair: Vendor B (180 SAR) - Saving 20 SAR (10%)
  - Total: 65,000 SAR
  - Total Savings: 5,000 SAR (7.1%)
User: Click "Apply Best Vendors"
```

**Day 7 (Quotation)**:
```
User: Click "Generate Sales Quotation"
User: Set margin 20%
User: Review preview:
  - Cost: 65,000 SAR
  - Margin: 13,000 SAR (20%)
  - Total: 78,000 SAR
User: Click "Generate Quotation"
System: Creates Sales Order
User: Send to customer
User: Click "Submit Tender"
```

**Day 14 (Customer Decision)**:
```
Customer: Accepts offer
User: Click "Mark as Won"
User: Enter winning reason
System: Updates CRM opportunity to Won
```

**Day 15 (Project Creation)**:
```
User: Click "Create Project"
User: Set project name "School Furniture Supply - Al-Riyadh School"
User: Assign Project Manager
User: Enable "Create Tasks from BoQ" ✓
User: Click "Create Project"
System: Creates project with 2 tasks:
  - Task 1: 100x School Desk
  - Task 2: 100x School Chair
```

---

## 🎓 Training Guide

### For Tender Users (1 Hour Training)

**Module 1: Etimad Portal Integration (15 min)**
- Understanding automatic scraping
- Viewing scraped tenders
- Creating opportunities

**Module 2: Tender Creation (15 min)**
- Creating from opportunity
- Filling tender details
- Understanding stages

**Module 3: BoQ Management (15 min)**
- Adding products
- Setting quantities and costs
- Technical specifications

**Module 4: Vendor Management (15 min)**
- Creating RFQs
- Entering vendor offers
- Using comparison wizard

### For Tender Managers (2 Hour Training)

**All User Topics** (1 hour)

**Plus:**

**Module 5: Advanced Features (30 min)**
- Customizing stages
- Managing teams and assignments
- Report generation

**Module 6: Integration Understanding (30 min)**
- CRM workflow
- Purchase integration
- Sales quotation process
- Project creation

---

## 📈 Benefits & ROI

### Time Savings

**Before (Manual Process)**:
- Tender search: 2 hours/day
- Data entry: 1 hour/tender
- Vendor comparison: 2 hours/tender
- Quotation creation: 1 hour/tender
- **Total: ~6 hours per tender**

**After (With ICS Solution)**:
- Tender search: Automatic (0 hours)
- Data entry: 10 minutes (auto-populated)
- Vendor comparison: 5 minutes (wizard)
- Quotation creation: 5 minutes (wizard)
- **Total: ~20 minutes per tender**

**ROI**: 95% time reduction per tender!

### Cost Savings

**Typical Company**:
- 20 tenders/month
- Previous: 120 hours/month
- New: 7 hours/month
- **Savings: 113 hours/month**

At 100 SAR/hour:
- **Monthly Savings: 11,300 SAR**
- **Annual Savings: 135,600 SAR**
- **Module Cost: €2,500 (~10,000 SAR)**
- **Payback Period: <1 month!**

### Quality Improvements

- ✅ No missed tenders (automatic scraping)
- ✅ Better vendor selection (comparison tool)
- ✅ Consistent margins (automated calculation)
- ✅ Complete audit trail (mail tracking)
- ✅ Faster response times (reduced manual work)

---

## 🔧 Customization Options

### Available Customizations (Additional Services)

1. **Custom Workflow Stages**
   - Add company-specific stages
   - Custom approval workflows
   - Stage-based email notifications

2. **Additional Reports**
   - Tender performance analysis
   - Vendor comparison matrix
   - Win/loss ratio reports
   - Custom financial reports

3. **Enhanced BoQ Features**
   - Import from Excel/CSV
   - Export to Excel
   - BoQ templates
   - Bulk editing tools

4. **Advanced Vendor Features**
   - Vendor portal access
   - Online bid submission
   - Vendor scoring system
   - Vendor performance tracking

5. **Integration Extensions**
   - Accounting integration
   - Inventory management
   - Custom external APIs
   - Third-party tender portals

6. **Arabic Localization**
   - Complete Arabic translation
   - Arabic reports
   - Hijri calendar full support
   - RTL interface optimization

7. **Mobile App**
   - Tender notifications
   - Quick tender review
   - Approval on mobile
   - Dashboard access

---

## 📞 Support & Services

### Included Support

- ✅ Installation assistance
- ✅ Basic configuration support
- ✅ Documentation
- ✅ Bug fixes (90 days)

### Professional Services (Additional)

- **Implementation Service**: €1,500
  - Server setup
  - Module installation
  - Data migration
  - User training (4 hours)

- **Customization Service**: €150/hour
  - Custom fields
  - Custom reports
  - Workflow modifications
  - Integration development

- **Training Service**: €100/hour
  - On-site training
  - Remote training
  - Custom training materials
  - Recorded sessions

- **Maintenance Contract**: €200/month
  - Priority support
  - Monthly updates
  - Performance optimization
  - Continuous improvements

---

## 📜 License & Pricing

### Module Licenses

**ics_etimad_tenders_crm**:
- License: LGPL-3 (Free & Open Source)
- Price: FREE
- Source: Included

**ics_tender_management**:
- License: OPL-1 (Odoo Proprietary License)
- Price: **€2,500** (One-time payment)
- Includes: Full source code, documentation, installation support
- Updates: Free for 1 year

### Package Deals

**Standard Package**: €2,500
- ics_tender_management module
- Installation support
- Basic training (2 hours)
- Documentation

**Professional Package**: €3,800 (Save €200)
- ics_tender_management module
- Full implementation service
- Advanced training (4 hours)
- Documentation
- 30 days priority support

**Enterprise Package**: €5,000 (Save €900)
- ics_tender_management module
- Full implementation service
- Complete training (8 hours)
- Custom workflow setup
- 1 custom report
- 90 days priority support
- 3 months maintenance

---

## 🌟 Why Choose ICS Solution?

### ✅ Proven Technology
- Built on Odoo 18 (Latest version)
- Uses standard Odoo patterns
- Easy to maintain and extend

### ✅ Saudi Market Focus
- Designed for Saudi tender process
- Etimad portal integration
- Hijri calendar support
- Arabic-ready (can be fully translated)

### ✅ Complete Solution
- End-to-end workflow
- All phases covered
- No gaps in process

### ✅ Professional Support
- Experienced Odoo developers
- Saudi market expertise
- Responsive support team

### ✅ Great ROI
- Fast payback period (<1 month)
- Significant time savings (95%)
- Improved win rate
- Better margins

---

## 📧 Contact Information

**iCloud Solutions**

🌐 **Website**: https://icloud-solutions.net
📧 **Email**: contact@icloud-solutions.net
📱 **WhatsApp**: +216 50 271 737

**Business Hours**:
- Sunday to Thursday: 9 AM - 6 PM (Riyadh Time)
- Friday & Saturday: Closed

**Response Time**:
- Email: Within 24 hours
- WhatsApp: Within 4 hours
- Emergency: Within 1 hour (for enterprise customers)

---

## 🎬 Next Steps

### 1. Schedule a Demo
Contact us to schedule a live demonstration of the complete system.

### 2. Trial Period
We can set up a demo environment for your team to test (7 days free).

### 3. Purchase & Installation
Once satisfied, purchase the module and we'll handle installation.

### 4. Training & Go-Live
We'll train your team and support your go-live process.

### 5. Ongoing Support
We're here to support your success with the system.

---

## 🙏 Thank You

Thank you for considering ICS Tender Management solution. We look forward to helping your business win more tenders and improve efficiency!

**Let's transform your tender management process together!**

---

*Document Version: 1.0*
*Last Updated: 2024-01-29*
*Author: iCloud Solutions*
*License: This document is proprietary to iCloud Solutions*
