# Tender Management Workflow Structure

This document outlines the chronological and logical organization of the Tender Management form tabs, aligned with the actual tender lifecycle workflow.

---

## 📋 Workflow Phases Overview

The tender form is now organized into **8 chronological phases** that match the real-world tender management process:

```
Draft → Qualification → Team Setup → BoQ → Approvals → Evaluation → Outcome → Notes
```

---

## 🔄 Detailed Phase Structure

### **Phase 1: Tender Information** (Draft Stage)
**Tab Name:** `1. Tender Information`  
**When Used:** Initial tender setup, from Etimad or manual entry  
**Key Activities:**
- Review tender announcement
- Purchase tender booklet
- Schedule site visit
- Submit initial inquiries

**Fields:**
- **Description & Scope**: Full tender description
- **Source & Method**: Etimad link, completion time, submission method
- **Booklet Purchase**: Price, purchase status, receipt, dates
- **Site Visit**: Required status, date, required documents
- **Inquiries**: Last inquiry date, required inquiries list

**Workflow States:** `draft`

---

### **Phase 2: Qualification & Decision** (Draft/Technical Stage)
**Tab Name:** `2. Qualification & Decision`  
**When Used:** Internal evaluation and participation decision  
**Key Activities:**
- Assign presales engineer
- Evaluate tender criteria
- Assess winning probability
- Decide whether to participate

**Fields:**
- **Evaluation**: Presales employee, evaluation criteria files, certifications, estimated value
- **Participation Decision**: Winning probability, client relationship, participation decision, non-participation reason, challenges

**Workflow States:** `draft`, `technical`

---

### **Phase 3: Team & Suppliers** (Technical Stage)
**Tab Name:** `3. Team & Suppliers`  
**When Used:** Assemble internal team and identify suppliers  
**Key Activities:**
- Assign responsible employees
- Build communication team
- Identify potential suppliers
- Contact vendors for quotations

**Fields:**
- **Responsible Team**: Tender employee, sales representative
- **Selected Suppliers**: Final selected suppliers (many2many tags)
- **Tender Communication Team**: Internal team with roles (employee, role, contact info, phone, notes)
- **Potential Suppliers**: External suppliers (partner, scope, evaluation score, status, contact details)

**Workflow States:** `technical`

---

### **Phase 4: Bill of Quantities** (Technical/Financial Stage)
**Tab Name:** `4. Bill of Quantities`  
**When Used:** Create detailed product/service breakdown  
**Key Activities:**
- Add products/services
- Set quantities and estimates
- Collect vendor offers
- Select best vendors

**Fields:**
- Product, Name, Quantity, UoM
- Estimated Cost, Selected Vendor, Vendor Price
- Import/Export BoQ functionality

**Workflow States:** `technical`, `financial`

---

### **Phase 5: Approvals & Documents** (Quotation Stage)
**Tab Name:** `5. Approvals & Documents`  
**When Used:** Prepare final quotation and obtain internal approvals  
**Key Activities:**
- Get management approvals
- Upload final documents
- Prepare submission files

**Fields:**
- **Management Approvals**: Direct manager, department manager, financial manager, CEO (toggle buttons)
- **Document Submission**: Documents uploaded status, file submission required, submission date, review documents

**Workflow States:** `quotation`

---

### **Phase 6: Offer Results & Evaluation** (Submitted/Evaluation Stage)
**Tab Name:** `6. Offer Results & Evaluation`  
**When Used:** After tender submission, during customer evaluation  
**Key Activities:**
- Track offer opening dates
- Monitor technical/financial offer status
- Handle extensions or negotiations

**Fields:**
- **Offer Opening Dates**: Technical opening, financial opening, competing companies file
- **Technical Offer Status**: Accepted status, rejection reason
- **Financial Offer Status**: Accepted status, rejection reason
- **Extensions & Negotiations**: Extension requested, awarded, rejection reason, discount requested

**Workflow States:** `submitted`, `evaluation`

---

### **Phase 7: Final Outcome** (Won/Lost/Cancelled Stage)
**Tab Name:** `7. Final Outcome`  
**When Used:** Final tender result  
**Key Activities:**
- Record win/loss details
- Document award information
- Manage appeals if lost

**Sections:**

#### **A. Award Details** (Visible when `state = 'won'`)
- Awarded company, amount, date, award letter
- Winning reason, actual revenue

#### **B. Lost Reason** (Visible when `state = 'lost'`)
- Detailed reason for losing

#### **C. Appeal Workflow** (Visible when `state = 'lost'`)
- Appeal submitted status
- Submission date, letter file, reason
- Appeal status (pending/accepted/rejected/withdrawn)
- Response date, response notes
- **Info Alert**: Shows when appeal is available (in Arabic and English)

**Workflow States:** `won`, `lost`, `cancelled`

---

### **Phase 8: Internal Notes** (All Stages)
**Tab Name:** `8. Internal Notes`  
**When Used:** Throughout entire tender lifecycle  
**Key Activities:**
- Document internal communications
- Record observations and decisions
- Track follow-ups

**Fields:**
- Free-text notes field

**Workflow States:** All states

---

## 🎯 Workflow State Mapping

| State | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Phase 7 | Phase 8 |
|-------|---------|---------|---------|---------|---------|---------|---------|---------|
| **Draft** | ✅ Primary | ✅ Primary | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ Always |
| **Technical** | ➖ | ✅ Active | ✅ Primary | ✅ Primary | ➖ | ➖ | ➖ | ✅ Always |
| **Financial** | ➖ | ➖ | ✅ Active | ✅ Primary | ➖ | ➖ | ➖ | ✅ Always |
| **Quotation** | ➖ | ➖ | ➖ | ✅ Active | ✅ Primary | ➖ | ➖ | ✅ Always |
| **Submitted** | ➖ | ➖ | ➖ | ➖ | ✅ Review | ✅ Primary | ➖ | ✅ Always |
| **Evaluation** | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ Primary | ➖ | ✅ Always |
| **Won** | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ Primary | ✅ Always |
| **Lost** | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ Primary | ✅ Always |
| **Cancelled** | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ Primary | ✅ Always |

**Legend:**
- ✅ **Primary**: Main phase for this state
- ✅ **Active**: Phase is actively used in this state
- ➖ **Review**: Phase can be reviewed but not primary focus
- ✅ **Always**: Always accessible

---

## 🔄 Typical Workflow Journey

### **Scenario 1: Supply Tender (Won)**
```
1. Tender Information (Draft)
   ↓ Purchase booklet, schedule site visit
2. Qualification & Decision (Draft → Technical)
   ↓ Evaluate and decide to participate
3. Team & Suppliers (Technical)
   ↓ Assign team, contact suppliers
4. Bill of Quantities (Technical → Financial)
   ↓ Create BoQ, collect vendor offers
5. Approvals & Documents (Financial → Quotation)
   ↓ Get approvals, prepare final quotation
6. Offer Results & Evaluation (Quotation → Submitted → Evaluation)
   ↓ Submit, track opening dates
7. Final Outcome (Evaluation → Won)
   ↓ Record award details
8. Internal Notes (Throughout)
   ✅ Project created automatically
```

### **Scenario 2: Services Tender (Lost with Appeal)**
```
1. Tender Information (Draft)
2. Qualification & Decision (Draft → Technical)
3. Team & Suppliers (Technical)
4. Bill of Quantities (Technical → Financial)
5. Approvals & Documents (Financial → Quotation)
6. Offer Results & Evaluation (Quotation → Submitted → Evaluation)
7. Final Outcome (Evaluation → Lost)
   ↓ Submit appeal
   ↓ Track appeal status
   ↓ Receive response
8. Internal Notes (Throughout)
```

---

## 🎨 UX Improvements

### **Before Reorganization:**
- ❌ No logical flow
- ❌ Information scattered across tabs
- ❌ Difficult to follow tender lifecycle
- ❌ Duplicate or misplaced fields

### **After Reorganization:**
- ✅ Chronological workflow structure
- ✅ Numbered phases (1-8)
- ✅ Phase names indicate when to use
- ✅ Fields grouped by activity
- ✅ Conditional visibility based on state
- ✅ Clear progression path
- ✅ Bilingual labels (Arabic + English)

---

## 📊 Benefits

1. **Intuitive Navigation**: Users follow the natural tender process
2. **Reduced Errors**: Right information at the right time
3. **Faster Data Entry**: Fields are grouped by activity, not by type
4. **Better Training**: New users understand the workflow quickly
5. **Compliance**: Ensures all steps are followed in order
6. **Audit Trail**: Clear history of tender progression
7. **Bilingual Support**: Full Arabic and English support

---

## 🚀 Version

**Module:** `ics_tender_management`  
**Version:** 18.0.2.2.0  
**Last Updated:** 2026-01-30  
**Odoo Version:** 18.0

---

## 📝 Notes

- All tabs are always accessible (no hard restrictions)
- Conditional visibility based on `state` field for certain sections
- Appeal workflow only appears when `state = 'lost'` or `'cancelled'`
- Internal Notes available at all times for documentation
- Automated activities trigger based on state changes (see `ACTIVITY_AUTOMATION_GUIDE.md`)

---

## 🔗 Related Documentation

- `ACTIVITY_AUTOMATION_GUIDE.md` - Automated activities per phase
- `PROJECT_AUTOMATION_SUMMARY.md` - Auto-project creation when won
- `CRM_SYNC_DOCUMENTATION.md` - CRM opportunity synchronization
- `WORKFLOW_GUIDE.md` - Detailed workflow implementation
- `LEGACY_MIGRATION_COMPLETE.md` - Field migration from legacy system
