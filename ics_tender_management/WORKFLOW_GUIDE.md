# ICS Tender Management - Complete Workflow Guide

**Version**: 18.0.2.0.0
**Date**: January 29, 2026
**Module**: ics_tender_management

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Tender Lifecycle Workflow](#tender-lifecycle-workflow)
4. [Supply Projects Workflow](#supply-projects-workflow)
5. [O&M Services Workflow](#om-services-workflow)
6. [Integration Workflows](#integration-workflows)
7. [Best Practices](#best-practices)
8. [Common Scenarios](#common-scenarios)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What This Module Does

The ICS Tender Management module provides end-to-end management of government tenders in Saudi Arabia, from opportunity identification through project execution and closure.

**Key Capabilities**:
- ✅ Tender opportunity management (pre-award)
- ✅ Technical and financial analysis
- ✅ Vendor quotation collection
- ✅ Quotation preparation and submission
- ✅ Project execution tracking (post-award)
- ✅ Procedure compliance monitoring
- ✅ Financial tracking and invoicing
- ✅ Etimad platform integration

---

## 👥 User Roles & Permissions

### Role 1: Tender Manager
**Access Level**: Full Access

**Responsibilities**:
- Create and manage tenders
- Approve technical studies
- Review vendor quotations
- Prepare final quotations
- Submit tenders
- Convert won tenders to projects

**Typical Tasks**:
- Monitor dashboard daily
- Review stage progression
- Approve quotations
- Track compliance

---

### Role 2: Technical Team
**Access Level**: Read + Technical Study

**Responsibilities**:
- Conduct technical analysis
- Review specifications
- Create Bill of Quantities (BoQ)
- Identify technical requirements
- Document technical notes

**Typical Tasks**:
- Import BoQ from Excel
- Define product specifications
- Calculate quantities
- Create technical documentation

---

### Role 3: Financial Team
**Access Level**: Read + Financial Study

**Responsibilities**:
- Collect vendor quotations
- Analyze pricing
- Calculate margins
- Prepare cost estimates
- Generate comparative analysis

**Typical Tasks**:
- Send RFQs to vendors
- Import vendor offers
- Compare vendor pricing
- Calculate final pricing

---

### Role 4: Sales Team
**Access Level**: Read + Create

**Responsibilities**:
- Identify opportunities
- Create initial tenders
- Monitor Etimad platform
- Import Etimad tenders
- Track submission deadlines

**Typical Tasks**:
- Browse Etimad tenders
- Import relevant opportunities
- Create tender records
- Set deadlines

---

### Role 5: Project Manager
**Access Level**: Project Management

**Responsibilities**:
- Execute won projects
- Manage project teams
- Track deliverables
- Prepare invoices
- Monitor SLAs (for O&M)

**Typical Tasks**:
- Create project from won tender
- Assign team members
- Track milestones
- Prepare financial claims

---

## 🔄 Tender Lifecycle Workflow

### Complete Lifecycle Overview

```
┌─────────────────────────────────────────────────────────┐
│                  TENDER LIFECYCLE                        │
└─────────────────────────────────────────────────────────┘

1️⃣ OPPORTUNITY IDENTIFICATION
   ├── Browse Etimad Platform
   ├── Manual Entry
   └── CRM Opportunity Import

2️⃣ TENDER REGISTRATION
   ├── Create Tender Record
   ├── Set Basic Information
   └── Assign Team

3️⃣ TECHNICAL STUDY
   ├── Review Specifications
   ├── Create/Import BoQ
   ├── Define Requirements
   └── Technical Approval

4️⃣ FINANCIAL STUDY
   ├── Send RFQs to Vendors
   ├── Collect Vendor Offers
   ├── Compare Pricing
   └── Select Best Offers

5️⃣ QUOTATION PREPARATION
   ├── Calculate Final Pricing
   ├── Add Margin
   ├── Generate Quotation
   └── Internal Review

6️⃣ SUBMISSION
   ├── Submit to Customer
   ├── Track Submission
   └── Wait for Evaluation

7️⃣ EVALUATION PERIOD
   ├── Customer Review
   ├── Answer Clarifications
   └── Wait for Decision

8️⃣ AWARD DECISION
   ├── Won → Create Project
   ├── Lost → Document Reasons
   └── Cancelled → Close Record

9️⃣ PROJECT EXECUTION (if Won)
   ├── Supply Projects → 6 Phases
   └── O&M Services → 6 Phases
```

---

## 📊 Stage-by-Stage Workflow

### Stage 1: Draft

**Objective**: Register tender opportunity and gather initial information

**Entry Criteria**:
- New opportunity identified
- Basic information available

**Activities**:

1. **Create Tender**
   ```
   Tenders → Create

   Required Fields:
   - Tender Name
   - Customer (res.partner)
   - Tender Category (supply/maintenance/services/etc.)
   - Tender Type (single_vendor/multiple_vendor)
   - Estimated Cost
   - Deadline Date
   ```

2. **Set Basic Information**
   - Reference number (if available)
   - Tender category
   - Customer details
   - Estimated budget
   - Submission deadline

3. **Attach Documents**
   - Tender documents from customer
   - Technical specifications
   - Terms and conditions
   - Any relevant files

4. **Assign Team**
   - Assign technical lead
   - Assign financial analyst
   - Set responsible manager

**Exit Criteria**:
- All basic information entered
- Documents attached
- Team assigned

**Next Stage**: Technical Study

---

### Stage 2: Technical Study

**Objective**: Complete technical analysis and create Bill of Quantities

**Entry Criteria**:
- Draft tender with complete information
- Technical specifications available

**Activities**:

1. **Review Specifications**
   - Analyze technical requirements
   - Identify scope of work
   - Note special requirements
   - Document technical challenges

2. **Create Bill of Quantities (BoQ)**

   **Option A: Manual Entry**
   ```
   Tender → BoQ Lines → Add Line

   For Each Item:
   - Product/Service
   - Description
   - Quantity
   - Unit of Measure
   - Notes
   ```

   **Option B: Import from Excel**
   ```
   Tender → Import BoQ

   Excel Format:
   | Product Code | Description | Quantity | UOM | Notes |

   Steps:
   1. Download template
   2. Fill Excel file
   3. Upload file
   4. Validate import
   5. Confirm
   ```

3. **Define Technical Requirements**
   - Product specifications
   - Quality standards
   - Delivery requirements
   - Testing/inspection needs
   - Warranty requirements

4. **Technical Risk Assessment**
   - Identify technical risks
   - Document mitigation plans
   - Note vendor capabilities needed
   - Special certifications required

**Exit Criteria**:
- BoQ complete and validated
- Technical requirements documented
- Risk assessment completed
- Technical team approval

**Next Stage**: Financial Study

---

### Stage 3: Financial Study

**Objective**: Collect vendor quotations and analyze pricing

**Entry Criteria**:
- Technical study complete
- BoQ finalized
- Vendors identified

**Activities**:

1. **Identify Vendors**
   ```
   For Single Vendor Type:
   - Select vendor(s) for entire tender

   For Multiple Vendor Type:
   - Select vendor(s) per BoQ line
   ```

2. **Send RFQs**

   **Single Vendor Tender**:
   ```
   Tender → Vendor Offers Tab → Add Vendor

   For Each Vendor:
   - Select vendor (res.partner)
   - Set deadline
   - Auto-send RFQ email
   ```

   **Multiple Vendor Tender (Product-wise)**:
   ```
   Tender → BoQ Lines → Select Line → Vendor Offers

   For Each Line:
   - Select vendor(s)
   - Request quotation
   - Set response deadline
   ```

3. **Collect Vendor Offers**

   **Manual Entry**:
   ```
   Vendor Offer → Edit
   - Enter offered price
   - Set validity period
   - Upload vendor quotation
   - Add notes
   - Mark as "Received"
   ```

   **Auto-Import** (if integrated):
   - Vendor submits online
   - System auto-captures pricing
   - Notification sent

4. **Vendor Comparison**
   ```
   Tender → Vendor Comparison Wizard

   View:
   - Vendor names
   - Quoted prices per line
   - Total values
   - Comparison matrix

   Select:
   - Best offers per line
   - Mark as "Accepted"
   ```

5. **Price Analysis**
   - Compare vendor pricing
   - Identify outliers
   - Negotiate if needed
   - Document assumptions
   - Calculate base cost

**Exit Criteria**:
- All vendor quotations received
- Pricing analysis completed
- Best offers selected
- Base cost calculated

**Next Stage**: Quotation Prepared

---

### Stage 4: Quotation Prepared

**Objective**: Calculate final pricing and generate customer quotation

**Entry Criteria**:
- Vendor offers finalized
- Base cost determined
- Margin policy defined

**Activities**:

1. **Calculate Final Pricing**
   ```
   For Each BoQ Line:
   - Vendor Price (from accepted offer)
   - + Margin % (company policy)
   - + Additional Costs
   - = Final Unit Price

   Total Quotation:
   - Sum of all line totals
   - + Taxes (if applicable)
   - = Grand Total
   ```

2. **Generate Quotation Document**
   ```
   Tender → Generate Quotation

   Options:
   - Create Sale Order
   - Create Purchase Requisition
   - Export to PDF

   Quotation Includes:
   - Company header
   - Customer details
   - BoQ with prices
   - Terms and conditions
   - Validity period
   - Delivery schedule
   ```

3. **Internal Review**
   - Financial review
   - Management approval
   - Legal review (if needed)
   - Final adjustments

4. **Quality Check**
   - Verify calculations
   - Check against customer requirements
   - Ensure competitiveness
   - Validate margins

**Exit Criteria**:
- Final pricing approved
- Quotation document generated
- Internal approval obtained
- Ready for submission

**Next Stage**: Submitted

---

### Stage 5: Submitted

**Objective**: Submit tender to customer and track submission

**Entry Criteria**:
- Quotation approved
- All documents prepared
- Deadline not passed

**Activities**:

1. **Submit to Customer**
   - Upload to customer portal (Etimad)
   - Email submission
   - Physical delivery (if required)
   - Obtain receipt acknowledgment

2. **Update Record**
   ```
   Tender → Set as Submitted

   Record:
   - Submission date
   - Submission method
   - Confirmation reference
   - Submitted by (user)
   ```

3. **Track Submission**
   - Monitor deadline
   - Check submission status
   - Confirm receipt
   - Keep communication log

4. **Post-Submission Tasks**
   - Archive submission documents
   - Brief management
   - Prepare for questions
   - Monitor evaluation timeline

**Exit Criteria**:
- Tender officially submitted
- Receipt confirmed
- Documents archived
- Team briefed

**Next Stage**: Under Evaluation

---

### Stage 6: Under Evaluation

**Objective**: Support customer evaluation and answer clarifications

**Entry Criteria**:
- Tender submitted
- Evaluation period started
- Waiting for customer feedback

**Activities**:

1. **Monitor Evaluation**
   - Track evaluation timeline
   - Check for customer queries
   - Monitor competitor activity
   - Stay prepared for clarifications

2. **Answer Clarifications**
   - Respond to customer questions
   - Provide additional documentation
   - Technical clarifications
   - Commercial clarifications
   - Keep response log

3. **Update Information**
   - Document all communications
   - Track changes/amendments
   - Update team on status
   - Prepare for presentation (if needed)

4. **Follow-up**
   - Regular customer contact
   - Status inquiries
   - Demonstrate commitment
   - Address concerns proactively

**Exit Criteria**:
- Evaluation completed
- Decision received
- Award/rejection notification

**Next Stage**: Won, Lost, or Cancelled

---

### Stage 7A: Won ✅

**Objective**: Celebrate success and initiate project execution

**Entry Criteria**:
- Official award letter received
- Contract signed
- Tender officially won

**Activities**:

1. **Receive Award Letter**
   ```
   Tender → Mark as Won

   Record:
   - Award date
   - Award letter reference
   - Contract value
   - Project start date
   - Attach award letter
   ```

2. **Celebration & Communication**
   - Notify team
   - Celebrate success
   - Brief management
   - Update stakeholders

3. **Project Creation**
   ```
   Tender → Create Project

   Wizard:
   - Project name (from tender)
   - Customer (from tender)
   - Project type (Supply/O&M)
   - Transfer BoQ as project tasks
   - Assign project manager
   - Set timeline
   ```

4. **Contract Setup**
   - Create sale order
   - Sign contract
   - Set payment terms
   - Define milestones

5. **Team Mobilization**
   - Assign project team
   - Kickoff meeting
   - Resource allocation
   - Schedule planning

**Exit Criteria**:
- Project created
- Team assigned
- Contract signed
- Execution started

**Next Step**: Project Execution (Supply or O&M workflow)

---

### Stage 7B: Lost ❌

**Objective**: Learn from loss and improve future performance

**Entry Criteria**:
- Official rejection received
- Tender not awarded

**Activities**:

1. **Document Loss**
   ```
   Tender → Mark as Lost

   Record:
   - Loss date
   - Reason(s) for loss
   - Winning competitor (if known)
   - Winning price (if available)
   - Lessons learned
   ```

2. **Loss Analysis**
   - Why did we lose?
   - Pricing too high?
   - Technical gaps?
   - Better competitor offer?
   - Relationship issues?

3. **Lessons Learned**
   - Document key learnings
   - Share with team
   - Update procedures
   - Improve for next time

4. **Customer Relationship**
   - Thank customer for opportunity
   - Request feedback
   - Maintain relationship
   - Keep door open for future

**Exit Criteria**:
- Loss documented
- Analysis completed
- Lessons captured
- Team debriefed

**Archive**: Tender closed and archived

---

### Stage 7C: Cancelled

**Objective**: Close cancelled tender properly

**Entry Criteria**:
- Tender cancelled by customer OR
- Company decides not to proceed

**Activities**:

1. **Document Cancellation**
   ```
   Tender → Mark as Cancelled

   Record:
   - Cancellation date
   - Reason for cancellation
   - Who cancelled (customer/company)
   - Costs incurred
   ```

2. **Close Activities**
   - Stop all work
   - Notify team
   - Close vendor RFQs
   - Archive documents

3. **Cost Recovery**
   - Document costs incurred
   - Claim if applicable
   - Close purchase orders

**Exit Criteria**:
- Cancellation documented
- All activities stopped
- Costs tracked

**Archive**: Tender closed and archived

---

## 🚚 Supply Projects Workflow (مشاريع التوريد)

### Overview
Applies to tenders for **supply of goods** (equipment, materials, products)

**Duration**: Typically 3-12 months
**Key Focus**: Delivery, quality inspection, handover

---

### Phase 1: استلام المشروع بعد الترسية
**Project Receipt After Award**

**Duration**: 1-2 weeks

**Entry Criteria**:
- Tender won
- Award letter received
- Contract signed

**Activities**:

1. **Project Initialization**
   ```
   Won Tender → Create Project

   Project Details:
   - Name: [Customer] - [Tender Name]
   - Type: Supply Project
   - Start Date: [Award Date]
   - Deadline: [Delivery Date]
   - Budget: [Contract Value]
   ```

2. **Review Requirements**
   - Review quantities from BoQ
   - Verify specifications
   - Check delivery locations
   - Confirm acceptance criteria
   - Document special requirements

3. **Determine Delivery Period**
   - Calculate lead times
   - Consider vendor availability
   - Factor in customs (if import)
   - Add buffer time
   - Set milestones

4. **Approve Supply Plan**
   ```
   Project → Tasks

   Create Tasks:
   - Contract vendor(s)
   - Place purchase orders
   - Vendor manufacturing/preparation
   - Quality inspection
   - Shipping/logistics
   - Delivery to customer
   - Preliminary acceptance
   - Final acceptance
   - Invoicing
   ```

5. **Assign Project Commissioner** (المفوض)
   - Assign project manager
   - Define authority levels
   - Set reporting structure

**Deliverables**:
- ✅ Project created in system
- ✅ Supply plan approved
- ✅ Timeline defined
- ✅ Team assigned

**Exit Criteria**:
- Project plan approved
- Resources allocated
- Ready to contract vendors

**Next Phase**: Contracting with Suppliers

---

### Phase 2: التعاقد مع الموردين
**Contracting with Suppliers**

**Duration**: 2-4 weeks

**Entry Criteria**:
- Project initiated
- Vendor selection completed
- Budget approved

**Activities**:

1. **Review Vendor Offers**
   - Review accepted offers from tender
   - Confirm pricing still valid
   - Check vendor availability
   - Verify delivery capability

2. **Issue Purchase Orders**
   ```
   For Single Vendor:
   Tender → Generate PO
   - Converts entire BoQ to single PO
   - Vendor: Selected vendor
   - Products: From BoQ
   - Quantities: From BoQ
   - Prices: From accepted offer

   For Multiple Vendors:
   - Generate PO per vendor
   - Each PO has relevant line items
   - Prices from respective offers
   ```

3. **Purchase Order Details**
   - Product specifications
   - Quantities
   - Unit prices
   - Total value
   - Delivery schedule
   - Quality requirements
   - Penalties for delay
   - Payment terms

4. **Contract Signing**
   - Send PO to vendor
   - Obtain vendor acceptance
   - Sign contract
   - Define delivery schedule
   - Set inspection criteria

5. **Track Material Readiness**
   ```
   Project → Purchase Orders

   Monitor:
   - PO confirmation status
   - Manufacturing progress
   - Quality checks at vendor
   - Estimated ready date
   ```

**Deliverables**:
- ✅ Purchase orders issued
- ✅ Contracts signed
- ✅ Delivery schedule confirmed
- ✅ Quality criteria defined

**Exit Criteria**:
- All POs confirmed
- Delivery dates set
- Vendor production started

**Next Phase**: Supply Execution

---

### Phase 3: تنفيذ التوريد
**Supply Execution**

**Duration**: Variable (4-20 weeks depending on products)

**Entry Criteria**:
- Vendor contracts signed
- Production/preparation started
- Delivery schedule confirmed

**Activities**:

1. **Receive Materials from Vendor**
   ```
   Monitor vendor progress:
   - Regular status updates
   - Site visits if needed
   - Quality checks during production
   - Pre-shipment inspection
   ```

2. **Goods Receipt**
   - Vendor notifies completion
   - Arrange logistics
   - Receive goods at warehouse
   - Initial inspection

3. **Inspect Quantities & Specifications**
   ```
   Purchase → Receipts → Validate

   Inspection Checklist:
   - ✅ Quantity matches PO
   - ✅ Specifications match requirements
   - ✅ Quality acceptable
   - ✅ Packaging intact
   - ✅ Documentation complete
   - ✅ Test certificates (if required)
   ```

4. **Coordinate with Government Entity**
   - Notify customer of readiness
   - Schedule delivery
   - Arrange site access
   - Coordinate inspection

5. **Document Delivery Minutes**
   ```
   For Each Delivery:
   - Delivery date and time
   - Location
   - Delivered items (quantities)
   - Inspection results
   - Customer acceptance
   - Signatures
   - Photos
   - Any discrepancies
   ```

**Deliverables**:
- ✅ Goods received from vendor
- ✅ Quality inspection completed
- ✅ Delivery to customer coordinated
- ✅ Delivery minutes documented

**Exit Criteria**:
- All items delivered to customer
- Customer preliminary acceptance
- Documentation complete

**Next Phase**: Preliminary Handover

---

### Phase 4: الاستلام الابتدائي
**Preliminary Handover**

**Duration**: 1-2 weeks

**Entry Criteria**:
- All items delivered
- Customer has inspected goods
- No major issues

**Activities**:

1. **Deliver Materials to Government Entity**
   - Final delivery coordination
   - Site installation (if required)
   - Setup and testing
   - Training (if required)

2. **Prepare Preliminary Receipt** (محضر الاستلام الابتدائي)
   ```
   Handover Document Includes:
   - Project details
   - Delivered items list
   - Quantities delivered
   - Location(s)
   - Delivery date
   - Inspection results
   - Test results
   - Customer representative signature
   - Company representative signature
   ```

3. **Address Observations**
   - Document any issues
   - Create action items
   - Assign responsibility
   - Set correction timeline
   - Track resolution

4. **Warranty Registration**
   - Provide warranty certificates
   - Register warranties
   - Provide user manuals
   - Share maintenance guides

**Deliverables**:
- ✅ Preliminary handover certificate
- ✅ Delivery documentation
- ✅ Warranties provided
- ✅ Training completed (if required)

**Exit Criteria**:
- Customer preliminary acceptance received
- Minor issues documented
- Warranty period started

**Next Phase**: Final Handover

---

### Phase 5: الاستلام النهائي
**Final Handover**

**Duration**: 1-4 weeks (after warranty period or issue resolution)

**Entry Criteria**:
- Preliminary acceptance completed
- All observations addressed
- Warranty period elapsed OR all issues resolved

**Activities**:

1. **Approve Final Handover**
   - Customer final inspection
   - Verify all observations closed
   - Confirm full satisfaction
   - Obtain final acceptance

2. **Deliver Guarantees/Warranties**
   - Final warranty documents
   - Maintenance contracts (if applicable)
   - Spare parts list
   - As-built documentation
   - Training certificates

3. **Close Purchase Orders**
   ```
   Purchase → Orders → Close

   For Each PO:
   - Verify all items received
   - Close receipts
   - Mark as done
   - Archive documents
   ```

4. **Final Documentation**
   ```
   Final Handover File:
   - Contract documents
   - Purchase orders
   - Delivery minutes
   - Preliminary handover
   - Final handover certificate
   - Test reports
   - Warranties
   - Training records
   - Photos/videos
   - Customer acceptance letters
   ```

**Deliverables**:
- ✅ Final handover certificate
- ✅ All warranties delivered
- ✅ Complete documentation package
- ✅ Customer final acceptance

**Exit Criteria**:
- Final acceptance certificate signed
- All obligations fulfilled
- Ready for invoicing

**Next Phase**: Invoicing and Closure

---

### Phase 6: المستخلصات والإقفال
**Invoicing and Closure**

**Duration**: 2-8 weeks

**Entry Criteria**:
- Final handover completed
- Customer acceptance received
- Ready to invoice

**Activities**:

1. **Prepare Financial Claims** (المستخلصات)
   ```
   Project → Create Invoice

   Invoice Based On:
   - Contract value
   - Delivered quantities
   - Approved pricing
   - Payment terms

   Invoice Details:
   - Customer
   - Contract reference
   - Line items (from BoQ)
   - Quantities delivered
   - Unit prices
   - Total amount
   - Tax (if applicable)
   - Payment terms
   ```

2. **Prepare Supporting Documents**
   - Contract copy
   - Delivery minutes
   - Handover certificates
   - Inspection reports
   - Test certificates
   - Photos
   - Any other required documents

3. **Submit on Etimad Platform** (منصة اعتماد)
   ```
   If project is government:
   - Login to Etimad
   - Create financial claim
   - Upload invoice
   - Attach supporting documents
   - Submit for approval
   - Track status
   ```

4. **Track Payment**
   ```
   Accounting → Invoices → Track

   Monitor:
   - Invoice submission date
   - Approval status
   - Expected payment date
   - Actual payment received
   - Payment reference
   ```

5. **Project Closure**
   ```
   Project → Close

   Closure Checklist:
   - ✅ All deliverables completed
   - ✅ Customer acceptance received
   - ✅ Invoices submitted
   - ✅ Payment received (or tracked)
   - ✅ All documents archived
   - ✅ Lessons learned documented
   - ✅ Team debriefed
   - ✅ Project marked as done
   ```

6. **Archive Project** (الأرشفة)
   - Create project archive file
   - Scan all physical documents
   - Upload to document management
   - Tag and categorize
   - Set retention period
   - Ensure compliance

**Deliverables**:
- ✅ Invoice submitted
- ✅ Payment tracked
- ✅ Project closed
- ✅ Documents archived

**Exit Criteria**:
- Payment received
- Project officially closed
- Complete archive created

**Project Complete**: ✅

---

## 🔧 O&M Services Workflow (مشاريع الصيانة والتشغيل)

### Overview
Applies to tenders for **maintenance and operation services**

**Duration**: Typically 6-36 months (long-term contracts)
**Key Focus**: Service delivery, SLA compliance, periodic reporting

---

### Phase 1: بدء المشروع (Kick-off)
**Project Start**

**Duration**: 2-4 weeks

**Entry Criteria**:
- Tender won
- Contract signed
- Service start date confirmed

**Activities**:

1. **Assign Commissioner** (تعيين المفوض)
   ```
   Project → Settings

   Assign:
   - Project Manager (Commissioner)
   - Authority level
   - Reporting responsibilities
   - Escalation path
   ```

2. **Review Scope of Work and SLA**
   - Service scope definition
   - Service Level Agreements (SLAs)
   - Key Performance Indicators (KPIs)
   - Response times
   - Resolution times
   - Availability requirements
   - Penalty clauses
   - Bonus clauses

3. **Approve Organizational Structure**
   ```
   Define Team Structure:
   - Project Manager
   - Site Supervisor(s)
   - Technicians (number and skills)
   - Support staff
   - Reporting hierarchy
   - Shift schedules (if 24/7)
   ```

4. **Form Work Team** (تشكيل فريق العمل)
   ```
   Project → Team

   For Each Team Member:
   - Name
   - Role
   - Qualifications
   - CV (required by customer)
   - Certifications
   - Shift assignment
   - Contact information
   ```

5. **Hold Kickoff Meeting** (عقد اجتماع بدء المشروع)
   ```
   Kickoff Meeting Agenda:
   - Project introduction
   - Scope review
   - Team introductions
   - Site access arrangements
   - Communication protocols
   - Escalation procedures
   - Reporting requirements
   - Q&A

   Meeting Minutes:
   - Date and attendees
   - Agenda items
   - Decisions made
   - Action items
   - Next steps
   ```

**Deliverables**:
- ✅ Project team formed
- ✅ Organizational structure approved
- ✅ Kickoff meeting completed
- ✅ Site access arranged
- ✅ Team CVs submitted

**Exit Criteria**:
- Team mobilized
- Site access granted
- Ready to start planning

**Next Phase**: Operational Planning

---

### Phase 2: التخطيط التشغيلي
**Operational Planning**

**Duration**: 2-3 weeks

**Entry Criteria**:
- Team mobilized
- Site access granted
- Kickoff completed

**Activities**:

1. **Approve Work Plan and Timeline** (اعتماد خطة العمل)
   ```
   Project → Planning

   Work Plan Includes:
   - Service delivery methodology
   - Resource allocation
   - Equipment and tools
   - Spare parts inventory
   - Quality assurance procedures
   - Safety procedures
   - Training plan
   - Communication plan
   ```

2. **Approve Visit/Patrol Schedule** (جدول الزيارات والدوريات)
   ```
   Project → Tasks → Schedule

   For Preventive Maintenance:
   - Asset list
   - Maintenance frequency (daily/weekly/monthly)
   - Maintenance tasks per asset
   - Assigned technician
   - Estimated duration

   For Patrols:
   - Patrol routes
   - Patrol frequency
   - Checklist items
   - Reporting requirements
   ```

3. **Determine Notification Mechanism** (آلية الإبلاغ والاستجابة)
   ```
   Define:
   - How customer reports issues
     • Phone hotline
     • Email
     • Mobile app
     • Ticketing system

   - Response procedures
     • Issue categorization
     • Priority assignment
     • Response time per priority
     • Escalation rules

   - Communication channels
     • Daily reports
     • Weekly summaries
     • Incident notifications
     • Emergency contacts
   ```

4. **Approve Risk Plan** (خطة المخاطر)
   ```
   Risk Management:

   For Each Risk:
   - Risk description
   - Probability (Low/Medium/High)
   - Impact (Low/Medium/High)
   - Mitigation plan
   - Contingency plan
   - Responsible person

   Common Risks:
   - Equipment failure
   - Staff shortage
   - Spare parts unavailability
   - Customer site access delays
   - Weather conditions
   - Safety incidents
   ```

**Deliverables**:
- ✅ Work plan approved
- ✅ Visit schedule defined
- ✅ Notification procedures established
- ✅ Risk plan documented

**Exit Criteria**:
- All plans approved by customer
- Team trained
- Ready to execute

**Next Phase**: Work Execution

---

### Phase 3: تنفيذ الأعمال
**Work Execution**

**Duration**: Ongoing (contract duration minus planning and closure)

**Entry Criteria**:
- All plans approved
- Team trained
- Service start date reached

**Activities**:

1. **Execute Work Per Approved Plan**
   ```
   Daily Operations:

   Preventive Maintenance:
   - Follow maintenance schedule
   - Complete maintenance tasks
   - Document work performed
   - Update asset records

   Corrective Maintenance:
   - Receive service requests
   - Assign to technician
   - Diagnose problem
   - Repair/replace
   - Test and verify
   - Close ticket

   Patrols:
   - Execute patrol rounds
   - Complete checklists
   - Document observations
   - Report issues
   ```

2. **Comply with SLA Indicators** (الالتزام بمؤشرات الأداء)
   ```
   Track KPIs:

   Response Time:
   - P1 (Critical): [X] minutes
   - P2 (High): [X] hours
   - P3 (Medium): [X] hours
   - P4 (Low): [X] days

   Resolution Time:
   - Average time to resolve
   - Per priority level

   Availability:
   - System/Equipment uptime %
   - Target: [X]%

   Quality:
   - First-time fix rate
   - Customer satisfaction score
   - Incident recurrence rate
   ```

3. **Document Completed Work** (توثيق الأعمال المنفذة)
   ```
   For Each Activity:

   Work Order:
   - Date and time
   - Asset/Location
   - Work type (preventive/corrective)
   - Technician name
   - Work performed
   - Parts used
   - Time spent
   - Before/after photos
   - Customer signature

   Store in System:
   Project → Tasks → Log Time
   - Task: [Work item]
   - Hours: [Time spent]
   - Description: [Work details]
   - Attachments: [Photos, documents]
   ```

4. **Manage Field Teams** (إدارة الفرق الميدانية)
   ```
   Team Management:

   Daily:
   - Assign work orders
   - Monitor progress
   - Track locations (if GPS)
   - Handle emergencies
   - Resolve issues

   Weekly:
   - Team meetings
   - Performance review
   - Training needs
   - Schedule adjustments
   ```

**Deliverables** (Ongoing):
- ✅ Services delivered per schedule
- ✅ SLAs maintained
- ✅ Work documented
- ✅ Issues resolved

**Exit Criteria** (For this phase):
- Contract period ongoing
- Continuous service delivery

**Next Phase**: Monitoring and Reporting (Parallel)

---

### Phase 4: المتابعة والتقارير
**Monitoring and Reporting**

**Duration**: Ongoing (parallel with execution)

**Entry Criteria**:
- Services being delivered
- Data being collected

**Activities**:

1. **Prepare Periodic Reports** (إعداد التقارير الدورية)

   **Daily Reports** (if required):
   ```
   Daily Summary:
   - Date
   - Work orders completed
   - Issues reported
   - Issues resolved
   - Technicians on duty
   - Notable incidents
   - Next day plan
   ```

   **Weekly Reports**:
   ```
   Weekly Report:
   - Week period
   - Total work orders
   - Preventive vs corrective split
   - SLA compliance %
   - Key achievements
   - Challenges faced
   - Upcoming activities
   ```

   **Monthly Reports**:
   ```
   Monthly Report:
   - Executive summary
   - Service statistics
   - SLA performance
   - KPI dashboard
   - Asset health status
   - Spare parts consumed
   - Team performance
   - Customer satisfaction
   - Recommendations
   - Photos
   ```

2. **Track Completion Percentage** (متابعة نسب الإنجاز)
   ```
   Project → Progress

   Track:
   - Scheduled tasks completed
   - Hours delivered vs planned
   - Milestones achieved
   - Overall completion %

   Monitor Against:
   - Contract requirements
   - Delivery schedule
   - SLA targets
   ```

3. **Address Observations** (معالجة الملاحظات)
   ```
   When Issues Arise:

   1. Document:
      - Issue description
      - Reported by
      - Date discovered
      - Impact/severity

   2. Analyze:
      - Root cause
      - Who is responsible
      - Correction needed

   3. Action:
      - Assign owner
      - Set deadline
      - Implement fix
      - Verify resolution

   4. Close:
      - Document closure
      - Customer approval
      - Prevent recurrence
   ```

4. **Continuous Coordination** (التنسيق المستمر)
   - Regular customer meetings
   - Status updates
   - Issue escalation
   - Change requests
   - Feedback collection

**Deliverables** (Periodic):
- ✅ Daily/Weekly/Monthly reports
- ✅ KPI dashboards
- ✅ Issues tracked and resolved
- ✅ Customer communications

**Ongoing**: Throughout contract period

---

### Phase 5: المستخلصات المالية
**Financial Invoicing**

**Duration**: Monthly or per contract terms

**Entry Criteria**:
- Service period completed (month/quarter)
- Work documented
- SLAs met

**Activities**:

1. **Prepare Invoices Per Contract** (إعداد المستخلصات)
   ```
   Monthly Invoice:

   Billing Basis:
   - Fixed monthly fee OR
   - Hours worked (T&M) OR
   - Work orders completed OR
   - Combination

   Invoice Line Items:
   - Service description
   - Period (e.g., January 2026)
   - Unit price
   - Quantity/Hours
   - Subtotal
   - Tax
   - Total

   Adjustments:
   - SLA penalties (if any)
   - Bonuses (if achieved)
   - Extra work charges
   - Deductions
   ```

2. **Prepare Supporting Documents**
   ```
   Attach to Invoice:
   - Monthly report
   - Work order summaries
   - Time sheets (if T&M)
   - SLA compliance report
   - Customer approval
   - Previous correspondence
   - Photos/evidence
   ```

3. **Submit to Government Entity**
   - Send invoice to customer
   - Obtain customer approval
   - Address any queries
   - Get invoice signed/stamped

4. **Submit on Etimad Platform** (منصة اعتماد)
   ```
   For Government Projects:
   - Login to Etimad
   - Create financial claim
   - Upload invoice
   - Attach supporting documents
   - Submit for approval
   - Track approval workflow
   - Monitor payment status
   ```

5. **Track Payment**
   ```
   Accounting → Customer Invoices

   Monitor:
   - Invoice submission date
   - Approval date
   - Payment due date
   - Payment received date
   - Amount received
   - Any discrepancies
   ```

**Deliverables** (Per Period):
- ✅ Invoice prepared
- ✅ Supporting documents attached
- ✅ Invoice submitted
- ✅ Payment tracked

**Repeat**: Monthly or per contract schedule

---

### Phase 6: التسليم والإقفال
**Handover and Closure**

**Duration**: 4-8 weeks

**Entry Criteria**:
- Contract period ending
- Final month invoiced
- Preparing for exit

**Activities**:

1. **Preliminary Handover** (التسليم الابتدائي)
   ```
   Before Contract End:

   Prepare:
   - Final service report
   - Asset status report
   - Maintenance history
   - Open issues list
   - Recommendations

   Handover Meeting:
   - Review contract period
   - Present final statistics
   - Discuss asset status
   - Address observations
   - Plan transition
   ```

2. **Transfer Knowledge** (نقل المعرفة)
   - Document procedures
   - Train customer staff (if required)
   - Share best practices
   - Provide recommendations
   - Transfer documentation

3. **Address Observations** (معالجة الملاحظات)
   - Resolve all open issues
   - Complete pending work
   - Address customer concerns
   - Obtain clearances

4. **Final Handover** (التسليم النهائي)
   ```
   Final Handover Certificate:

   Includes:
   - Contract summary
   - Service period
   - Total work delivered
   - SLA compliance summary
   - Asset condition report
   - Spare parts inventory (if handover)
   - Final statistics
   - Customer satisfaction rating
   - Signatures and stamps
   ```

5. **Close and Archive** (الإقفال والأرشفة)
   ```
   Project Closure:

   Financial:
   - Final invoice submitted
   - All payments received
   - Account reconciliation
   - Close project financially

   Operational:
   - Demobilize team
   - Return equipment
   - Close site access
   - Final report

   Documentation:
   - Archive all project files
   - Scan physical documents
   - Upload to system
   - Tag and categorize
   - Lessons learned
   - Team debrief

   System:
   - Mark project as complete
   - Archive in system
   - Update compliance metrics
   ```

**Deliverables**:
- ✅ Final handover certificate
- ✅ Complete documentation
- ✅ Knowledge transfer completed
- ✅ All payments received
- ✅ Project archived

**Exit Criteria**:
- Customer final acceptance
- Contract obligations fulfilled
- Project officially closed

**Project Complete**: ✅

---

## 🔗 Integration Workflows

### Integration 1: CRM to Tender

**Scenario**: Convert a CRM opportunity to a tender

**Workflow**:
```
CRM → Opportunities → Select Opportunity → Convert to Tender

Wizard:
- Tender name (from opportunity)
- Customer (from opportunity)
- Estimated cost (from opportunity)
- Tender category (select)
- Deadline (set)
- Notes (from opportunity)

Result:
- Tender created in Draft stage
- Linked to CRM opportunity
- Basic information pre-filled
```

---

### Integration 2: Etimad Platform to Tender

**Scenario**: Import tender from Etimad platform

**Workflow**:
```
Etimad Tenders → Browse → Select Tender → Import

System:
- Fetches tender details from Etimad
- Creates tender record
- Populates fields automatically:
  • Name
  • Reference number
  • Customer
  • Description
  • Deadline
  • Estimated budget

User:
- Reviews imported data
- Adds missing information
- Assigns team
- Marks as "Imported"
```

---

### Integration 3: Tender to Purchase

**Scenario**: Create purchase orders from tender

**Workflow**:
```
Tender (Financial Study stage) → Generate Purchase Orders

Options:

A) Generate RFQ (Request for Quotation):
   - Creates purchase requisition
   - Vendor selection mode
   - BoQ lines → RFQ lines
   - Send to multiple vendors
   - Collect bids

B) Direct Purchase Order:
   - Vendor already selected
   - BoQ lines → PO lines
   - Prices from accepted offers
   - Ready to confirm
```

---

### Integration 4: Tender to Sale Order

**Scenario**: Create customer quotation/sale order

**Workflow**:
```
Tender (Quotation Prepared stage) → Generate Quotation

Wizard:
- Customer (from tender)
- Products (from BoQ)
- Quantities (from BoQ)
- Prices (calculated with margin)

Creates:
- Sale Order in Draft
- Lines from BoQ
- Linked to tender
- Ready to send

Customer Accepts:
- Confirm sale order
- Mark tender as Won
```

---

### Integration 5: Won Tender to Project

**Scenario**: Create project from won tender

**Workflow**:
```
Tender (Won stage) → Create Project

Wizard:
- Project name (from tender)
- Customer (from tender)
- Project type (Supply/O&M)
- Budget (from tender)
- Timeline (set)

Options:
- Transfer BoQ as project tasks
- Assign project manager
- Copy tender documents

Result:
- Project created
- Linked to tender
- Tasks created from BoQ
- Team can start execution
```

---

## 💡 Best Practices

### General Best Practices

1. **Complete Information Early**
   - Fill all required fields in Draft stage
   - Attach all customer documents
   - Set realistic deadlines
   - Assign team immediately

2. **Use Templates**
   - Create tender templates for common types
   - Standard BoQ items
   - Standard pricing margins
   - Document templates

3. **Regular Updates**
   - Update tender status daily
   - Move to next stage promptly
   - Keep timeline accurate
   - Document all changes

4. **Document Everything**
   - Attach all correspondence
   - Save email communications
   - Upload customer documents
   - Keep audit trail

5. **Communication**
   - Use system for team communication
   - Log all customer interactions
   - Share important updates
   - Clear escalation path

---

### Technical Study Best Practices

1. **BoQ Quality**
   - Clear product descriptions
   - Accurate quantities
   - Correct units of measure
   - Detailed specifications
   - Reference standards

2. **Import Efficiency**
   - Use Excel import for large BoQs
   - Validate data before import
   - Clean up imported data
   - Add notes where needed

3. **Technical Documentation**
   - Attach technical specs
   - Reference standards/codes
   - Note special requirements
   - Document assumptions

---

### Financial Study Best Practices

1. **Vendor Management**
   - Send RFQs to multiple vendors
   - Set clear response deadlines
   - Follow up proactively
   - Document all offers

2. **Pricing Analysis**
   - Use vendor comparison tool
   - Document outliers
   - Justify selections
   - Keep audit trail

3. **Margin Calculation**
   - Follow company policy
   - Consider all costs
   - Include contingency
   - Be competitive

---

### Project Execution Best Practices

1. **Detailed Planning**
   - Break down into phases
   - Create detailed tasks
   - Assign responsibilities
   - Set milestones

2. **Regular Monitoring**
   - Daily progress checks
   - Weekly team meetings
   - Monthly reviews
   - Dashboard monitoring

3. **Documentation**
   - Log all work performed
   - Take photos/videos
   - Customer signatures
   - Time tracking

4. **SLA Compliance** (for O&M)
   - Track response times
   - Monitor KPIs daily
   - Address issues immediately
   - Report transparently

---

## 🎬 Common Scenarios

### Scenario 1: Rush Tender (Short Deadline)

**Situation**: Tender deadline is 3 days away

**Workflow**:
```
Day 1:
- Create tender immediately
- Assign full team
- Parallel technical & financial study
- Import BoQ from similar tender
- Send RFQs immediately

Day 2:
- Collect vendor offers
- Quick pricing analysis
- Calculate margins
- Prepare quotation

Day 3 (Morning):
- Final review
- Management approval
- Prepare submission documents

Day 3 (Afternoon):
- Submit before deadline
```

**Tips**:
- Use templates
- Work in parallel
- Skip non-essentials
- Focus on winning

---

### Scenario 2: Large Complex Tender

**Situation**: Large government project, 200+ BoQ items

**Workflow**:
```
Week 1:
- Create tender
- Assign extended team
- Import BoQ from Excel
- Break BoQ into categories
- Assign categories to team members

Week 2-3:
- Technical analysis per category
- Vendor identification
- Send RFQs in batches
- Start collecting offers

Week 4-5:
- Complete vendor offers
- Detailed pricing analysis
- Vendor comparison
- Best offer selection

Week 6:
- Final pricing calculation
- Margin optimization
- Quotation preparation
- Multiple review rounds

Week 7:
- Final approval
- Document preparation
- Submit tender
```

---

### Scenario 3: Tender Lost, Later Re-tendered

**Situation**: Lost a tender, customer re-tenders after 6 months

**Workflow**:
```
Original Tender:
- Marked as Lost
- Documented loss reasons
- Saved all data

Re-tender:
- Create new tender
- Copy from previous tender
- Update information
- Review previous loss reasons
- Adjust strategy
- Improve pricing
- Strengthen proposal
- Submit improved offer
```

**Advantages**:
- All data available
- Lessons learned applied
- Faster preparation
- Better pricing
- Higher win chance

---

### Scenario 4: Won Tender, Customer Delays

**Situation**: Tender won, but customer delays contract signing

**Workflow**:
```
Mark as Won:
- Record win date
- Note contract pending

While Waiting:
- Keep tender record active
- Do NOT create project yet
- Maintain vendor relationships
- Re-confirm pricing validity
- Update team on status

When Contract Signed:
- Update tender with contract info
- Create project
- Start execution
```

---

### Scenario 5: Mid-Project Scope Change (O&M)

**Situation**: Customer requests additional services mid-contract

**Workflow**:
```
Request Received:
- Document request
- Create change request

Analysis:
- Technical feasibility
- Resource requirements
- Cost impact
- Schedule impact

Negotiation:
- Prepare quotation
- Additional cost
- Timeline impact
- Contract amendment

Approval:
- Customer approval
- Contract amendment signed
- Update project scope
- Update BoQ/Tasks
- Continue execution
```

---

## 🔧 Troubleshooting

### Issue 1: Cannot Move to Next Stage

**Symptoms**:
- Stage button disabled OR
- Error when changing stage

**Possible Causes**:
1. Required fields missing
2. No BoQ lines
3. No vendor offers (in financial stage)
4. Insufficient permissions

**Solutions**:
```
Check:
1. All required fields filled?
2. BoQ has at least one line?
3. Vendor offers exist (if needed)?
4. User has correct permissions?
5. Workflow validations passing?

If still stuck:
- Contact system admin
- Check workflow customizations
```

---

### Issue 2: Vendor Offers Not Appearing

**Symptoms**:
- Vendor offers exist but not showing
- Cannot select best offer

**Solutions**:
```
1. Refresh page
2. Check filters (might be hiding offers)
3. Verify offer status (should be "Received" or "Accepted")
4. Check vendor offer dates (might be expired)
5. Clear browser cache
```

---

### Issue 3: Cannot Create Project from Won Tender

**Symptoms**:
- "Create Project" button missing OR
- Error when creating project

**Possible Causes**:
1. Tender not actually in Won stage
2. Project already created
3. Missing project module
4. Permission issues

**Solutions**:
```
Check:
1. Tender stage is "Won" (stage_id.is_won = True)?
2. No project already linked (tender_id field in projects)?
3. Project module installed?
4. User has project creation rights?

If issue persists:
- Check system logs
- Contact administrator
```

---

### Issue 4: Dashboard Not Loading

**Symptoms**:
- Dashboard shows loading spinner forever
- Dashboard shows blank page

**Solutions**:
```
1. Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
2. Clear browser cache
3. Try different browser
4. Check console for errors (F12)
5. Verify dashboard assets loaded:
   - Settings → Technical → Views → Search "tender_dashboard"
6. Regenerate assets:
   - Settings → Technical → Regenerate Assets
```

---

### Issue 5: SLA Tracking Not Working (O&M)

**Symptoms**:
- SLA violations not detected
- KPIs showing wrong values

**Solutions**:
```
Check Configuration:
1. SLA rules defined in project settings?
2. Task priorities set correctly?
3. Response/resolution times configured?
4. Automated actions enabled?

Verify Data:
1. Tasks have correct timestamps?
2. Task status updated properly?
3. Customer notifications sent?

Recalculate:
1. Run manual SLA calculation
2. Check scheduled actions
3. Review system logs
```

---

## 📞 Support & Help

### Getting Help

1. **Documentation**
   - Read this workflow guide
   - Check DASHBOARD_QUICK_START.md
   - Review DASHBOARD_IMPLEMENTATION.md

2. **System Admin**
   - Contact your Odoo administrator
   - Check system logs
   - Review user permissions

3. **Module Developer**
   - Email: contact@icloud-solutions.net
   - Website: https://icloud-solutions.net

4. **Odoo Community**
   - Odoo forums
   - Odoo documentation
   - Community modules

---

## 📚 Additional Resources

### Related Documentation

1. **User Guides**
   - DASHBOARD_QUICK_START.md - Dashboard usage
   - README_DASHBOARD.md - Overview

2. **Technical Documentation**
   - DASHBOARD_IMPLEMENTATION.md - Technical details
   - PROCEDURE_COMPLIANCE_IMPLEMENTATION.md - ICS procedures

3. **Compliance**
   - SPECIFICATION_COMPLIANCE_REPORT.md - Full compliance report
   - إجراء ادارة المشاريع (توريد) - Supply procedure (PDF)
   - إجراء ادارة المشاريع (صيانة و تشغيل) - O&M procedure (PDF)

---

## ✅ Workflow Checklist

### For Tender Managers

**Daily**:
- [ ] Check dashboard for updates
- [ ] Review active tenders
- [ ] Move tenders to next stage when ready
- [ ] Respond to team queries
- [ ] Update management on progress

**Weekly**:
- [ ] Review pipeline
- [ ] Check upcoming deadlines
- [ ] Review vendor offers
- [ ] Approve quotations
- [ ] Track submissions

**Monthly**:
- [ ] Analyze win/loss ratio
- [ ] Review compliance metrics
- [ ] Team performance review
- [ ] Process improvements

---

### For Project Managers

**Daily**:
- [ ] Review project tasks
- [ ] Monitor SLA compliance
- [ ] Address team issues
- [ ] Update project status
- [ ] Customer communication

**Weekly**:
- [ ] Team meetings
- [ ] Progress reports
- [ ] Issue resolution
- [ ] Resource planning

**Monthly**:
- [ ] Prepare monthly reports
- [ ] Invoice preparation
- [ ] Customer review meetings
- [ ] Performance analysis

---

## 🎯 Success Metrics

### Tender Success Metrics

- **Win Rate**: Target ≥ 40%
- **Average Tender Duration**: Target ≤ 4 weeks
- **On-time Submission**: Target ≥ 95%
- **Vendor Response Rate**: Target ≥ 80%

### Project Success Metrics

- **SLA Compliance**: Target ≥ 98% (O&M)
- **On-time Delivery**: Target ≥ 90% (Supply)
- **Customer Satisfaction**: Target ≥ 4.5/5
- **Procedure Compliance**: Target 100%

---

## 📋 Conclusion

This workflow guide provides comprehensive coverage of the ICS Tender Management module. By following these workflows, your organization can:

✅ Manage tenders efficiently
✅ Ensure procedure compliance
✅ Track project execution
✅ Maintain quality standards
✅ Achieve success targets

**Remember**: The system is a tool to support your processes. Adapt these workflows to your specific needs while maintaining compliance with ICS procedures.

---

**Developed by**: iCloud Solutions
**Version**: 18.0.2.0.0
**Last Updated**: January 29, 2026

*Complete Workflow Guide - For Success in Tender Management* 🎯
