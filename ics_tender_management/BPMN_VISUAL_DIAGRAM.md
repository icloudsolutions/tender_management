# ICS Tender Management - Visual BPMN Diagram

**Version**: 18.0.2.0.0
**Date**: January 29, 2026
**Format**: ASCII Art / Text Representation

---

## 🎯 Complete Process Flow

### Main Process Overview

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      ICS TENDER MANAGEMENT PROCESS                             │
│                         BPMN 2.0 Complete Workflow                             │
└────────────────────────────────────────────────────────────────────────────────┘


    ⭕ START
     │
     │ Opportunity Identified
     ↓
┌──────────────────┐
│  REGISTER TENDER │  📋 User Task
│   (Draft Stage)  │  ━━━━━━━━━━━━━━
└──────────────────┘  - Create tender record
     │                - Enter basic info
     │                - Attach documents
     ↓                - Assign team
┌──────────────────┐
│ TECHNICAL STUDY  │  📋 User Task
│                  │  ━━━━━━━━━━━━━━
└──────────────────┘  - Review specs
     │                - Create BoQ
     │                - Technical approval
     ↓
┌──────────────────┐
│ FINANCIAL STUDY  │  📋 User Task
│                  │  ━━━━━━━━━━━━━━
└──────────────────┘  - Identify vendors
     │                - Prepare RFQ
     ↓
┌──────────────────┐
│   SEND RFQ TO    │  ⚙️ Service Task
│     VENDORS      │  ━━━━━━━━━━━━━━━━
└──────────────────┘  - Auto-send emails
     │                - Track delivery
     ↓
     │ ⇢⇢⇢ RFQ Messages to Vendors ⇢⇢⇢
     ↓
┌──────────────────┐
│ COLLECT VENDOR   │  📋 User Task
│     OFFERS       │  ━━━━━━━━━━━━━━
└──────────────────┘  - Receive quotes
     │                - Enter in system
     ↓
     │ ⇠⇠⇠ Vendor Quotations Received ⇠⇠⇠
     ↓
┌──────────────────┐
│ COMPARE VENDOR   │  📋 User Task
│     OFFERS       │  ━━━━━━━━━━━━━━
└──────────────────┘  - Use wizard
     │                - Analyze pricing
     ↓
┌──────────────────┐
│ SELECT BEST      │  📋 User Task
│    VENDORS       │  ━━━━━━━━━━━━━━
└──────────────────┘  - Choose winners
     │                - Apply to BoQ
     ↓
┌──────────────────┐
│ PREPARE CUSTOMER │  📋 User Task
│    QUOTATION     │  ━━━━━━━━━━━━━━
└──────────────────┘  - Calculate prices
     │                - Add margin
     │                - Generate document
     ↓
     ◇
    ╱ ╲  Quotation
   ╱   ╲  Approved?
  ╱     ╲
 ╱   ?   ╲
╱─────────╲
     │
     ├─── NO ──→ [REVISE QUOTATION] ───┐
     │                                   │
     │                                   ↓
     ↓                                  (loop back)
    YES
     │
     ↓
┌──────────────────┐
│ SUBMIT TENDER TO │  📋 User Task
│    CUSTOMER      │  ━━━━━━━━━━━━━━
└──────────────────┘  - Submit via Etimad
     │                - Email/physical
     │                - Get confirmation
     ↓
     │ ⇢⇢⇢ Tender Submission to Etimad ⇢⇢⇢
     ↓
┌──────────────────┐
│ UNDER EVALUATION │  📋 User Task
│                  │  ━━━━━━━━━━━━━━
└──────────────────┘  - Monitor status
     │                - Answer questions
     │                - Provide docs
     ↓
     │ ⇠⇠⇠ Clarification Requests ⇠⇠⇠
     │ ⇢⇢⇢ Clarification Responses ⇢⇢⇢
     ↓
     ◇
    ╱ ╲  Tender
   ╱   ╲ Decision?
  ╱     ╲
 ╱   ?   ╲
╱─────────╲
     │
     ├─── WON ──────→ [Continue to Project] ────┐
     │                                           │
     ├─── LOST ─────→ [DOCUMENT LOSS] → ⭕ END  │
     │                                           │
     └─── CANCELLED → [DOC CANCELLATION] → ⭕ END │
                                                 │
                                                 ↓
                    [Award Letter Received] ⇠⇠⇠ From Customer
                                                 │
                                                 ↓
                                                 ◇
                                                ╱ ╲
                                               ╱   ╲ Project
                                              ╱     ╲ Type?
                                             ╱   ?   ╲
                                            ╱─────────╲
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                 SUPPLY                          │                          O&M
                PROJECT                          │                       SERVICES
                    │                            │                            │
                    ↓                            │                            ↓
            [See Supply Flow]                    │                   [See O&M Flow]
                    │                            │                            │
                    ↓                            │                            ↓
               ⭕ END                            │                       ⭕ END
```

---

## 🚚 Supply Projects Workflow (مشاريع التوريد)

### 6 Phases - Complete Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        SUPPLY PROJECTS (مشاريع التوريد)                      │
│                              6 Phase Workflow                                │
└──────────────────────────────────────────────────────────────────────────────┘

    ⭕ START (Tender Won - Supply Type)
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 1: PROJECT RECEIPT AFTER AWARD (استلام المشروع بعد الترسية)         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Create project from won tender
     │ • Review requirements and quantities
     │ • Determine delivery period
     │ • Approve supply plan
     │ • Assign project commissioner (المفوض)
     │
     │ Duration: 1-2 weeks
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 2: CONTRACTING WITH SUPPLIERS (التعاقد مع الموردين)                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Review vendor offers (from tender)
     │ • Issue purchase orders
     │ • Sign vendor contracts
     │ • Define delivery schedule
     │ • Track material readiness
     │
     │ Duration: 2-4 weeks
     │
     ↓
     │ ⇢⇢⇢ Purchase Orders to Vendors ⇢⇢⇢
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 3: SUPPLY EXECUTION (تنفيذ التوريد)                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Receive materials from vendor
     │ • Inspect quantities & specifications
     │ • Coordinate with government entity
     │ • Document delivery minutes
     │
     │ Duration: 4-20 weeks (varies by product)
     │
     ↓
     │ ⇠⇠⇠ Material Delivery from Vendors ⇠⇠⇠
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 4: PRELIMINARY HANDOVER (الاستلام الابتدائي)                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Deliver materials to government entity
     │ • Prepare preliminary receipt (محضر الاستلام الابتدائي)
     │ • Address observations
     │ • Register warranties
     │
     │ Duration: 1-2 weeks
     │
     ↓
     │ ⇢⇢⇢ Preliminary Handover to Customer ⇢⇢⇢
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 5: FINAL HANDOVER (الاستلام النهائي)                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Approve final handover
     │ • Deliver guarantees/warranties
     │ • Close purchase orders
     │ • Complete final documentation
     │
     │ Duration: 1-4 weeks
     │
     ↓
     │ ⇢⇢⇢ Final Handover Certificate to Customer ⇢⇢⇢
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 6: INVOICING AND CLOSURE (المستخلصات والإقفال)                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Prepare financial claims (المستخلصات)
     │ • Submit on Etimad platform
     │ • Track payment
     │ • Archive project (الأرشفة)
     │
     │ Duration: 2-8 weeks
     │
     ↓
     │ ⇢⇢⇢ Invoice Submission to Etimad ⇢⇢⇢
     │ ⇠⇠⇠ Payment from Customer ⇠⇠⇠
     │
     ↓
    ⭕ END - Supply Project Complete

┌────────────────────────────────────────┐
│ TOTAL DURATION: 3-12 months typically  │
│ COMPLIANCE: 100% ICS Procedure         │
└────────────────────────────────────────┘
```

---

## 🔧 O&M Services Workflow (مشاريع الصيانة والتشغيل)

### 6 Phases - Complete Flow with Loop

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   O&M SERVICES (مشاريع الصيانة والتشغيل)                    │
│                              6 Phase Workflow                                │
└──────────────────────────────────────────────────────────────────────────────┘

    ⭕ START (Tender Won - O&M Type)
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 1: PROJECT KICKOFF (بدء المشروع)                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Assign project commissioner (تعيين المفوض)
     │ • Review scope of work and SLA
     │ • Approve organizational structure
     │ • Form work team (تشكيل فريق العمل)
     │ • Hold kickoff meeting (عقد اجتماع بدء المشروع)
     │
     │ Duration: 2-4 weeks
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 2: OPERATIONAL PLANNING (التخطيط التشغيلي)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Approve work plan and timeline (اعتماد خطة العمل)
     │ • Approve visit/patrol schedule (جدول الزيارات والدوريات)
     │ • Determine notification mechanism (آلية الإبلاغ والاستجابة)
     │ • Approve risk plan (خطة المخاطر)
     │
     │ Duration: 2-3 weeks
     │
     ↓
     ┌─────────────────────────────────────────────────────────┐
     │                CONTINUOUS SERVICE LOOP                  │
     │               (Throughout Contract Period)              │
     └─────────────────────────────────────────────────────────┘
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 3: WORK EXECUTION (تنفيذ الأعمال)                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities (Ongoing):
     │ • Execute work per approved plan
     │ • Comply with SLA indicators
     │ • Document completed work
     │ • Manage field teams (إدارة الفرق الميدانية)
     │
     │ Duration: Ongoing (contract duration)
     │
     ↓
     │ ║
     │ ║  PARALLEL EXECUTION
     │ ║
     ↓ ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 4: MONITORING AND REPORTING (المتابعة والتقارير)                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities (Parallel with Phase 3):
     │ • Prepare periodic reports (إعداد التقارير الدورية)
     │   - Daily reports (if required)
     │   - Weekly reports
     │   - Monthly reports
     │ • Track completion percentage (متابعة نسب الإنجاز)
     │ • Address observations (معالجة الملاحظات)
     │ • Continuous coordination (التنسيق المستمر)
     │
     │ Duration: Ongoing (parallel with execution)
     │
     ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 5: FINANCIAL INVOICING (المستخلصات المالية)                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities (Periodic - Monthly/Quarterly):
     │ • Prepare invoices per contract (إعداد المستخلصات)
     │ • Submit to government entity
     │ • Submit on Etimad platform
     │ • Track payment
     │
     │ Duration: Monthly or per contract terms
     │
     ↓
     │ ⇢⇢⇢ Monthly Invoice to Etimad ⇢⇢⇢
     │ ⇠⇠⇠ Monthly Payment from Customer ⇠⇠⇠
     │
     ↓
     ◇
    ╱ ╲  Contract
   ╱   ╲  Period
  ╱     ╲  End?
 ╱   ?   ╲
╱─────────╲
     │
     ├─── NO: Continue Service ──┐
     │                            │
     │    (Loop back to Phase 3)  │
     │    ←←←←←←←←←←←←←←←←←←←←←←←←←┘
     │
     └─── YES: Proceed to Closure
          │
          ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PHASE 6: HANDOVER AND CLOSURE (التسليم والإقفال)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
     │
     │ Activities:
     │ • Preliminary handover (التسليم الابتدائي)
     │ • Transfer knowledge (نقل المعرفة)
     │ • Address observations (معالجة الملاحظات)
     │ • Final handover (التسليم النهائي)
     │ • Close and archive (الإقفال والأرشفة)
     │
     │ Duration: 4-8 weeks
     │
     ↓
     │ ⇢⇢⇢ Final Handover to Customer ⇢⇢⇢
     │
     ↓
    ⭕ END - O&M Service Complete

┌────────────────────────────────────────┐
│ TOTAL DURATION: 6-36 months typically  │
│ REPEATING: Phases 3-5 loop monthly     │
│ COMPLIANCE: 100% ICS Procedure         │
└────────────────────────────────────────┘
```

---

## 📊 Legend

### Symbols Used

```
⭕     Start/End Event
│ ↓    Sequence Flow (Forward)
←     Sequence Flow (Backward/Loop)
◇     Gateway (Decision Point)
╱ ╲
╱   ╲   Gateway Diamond Shape
╱─────╲
┌─────┐
│     │  User Task (Rounded Rectangle)
└─────┘
⚙️      Service Task (Automated)
📋     User Task Indicator
⇢⇢⇢    Message Flow (Outgoing)
⇠⇠⇠    Message Flow (Incoming)
║      Parallel Flow Indicator
┏━━━┓
┃   ┃  Phase Container (Bold Box)
┗━━━┛
```

### Task Types

- **📋 User Task**: Requires human action
- **⚙️ Service Task**: Automated by system
- **◇ Gateway**: Decision/branching point
- **⇢ Message Flow**: Communication between participants

---

## 🎯 Process Summary

### Complete Statistics

```
┌─────────────────────────────────────────────────────┐
│           PROCESS COMPLEXITY METRICS                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Total Activities:              35 tasks            │
│  User Tasks:                    32 tasks            │
│  Service Tasks:                  1 task             │
│  Gateways:                       3 decisions        │
│  End Events:                     4 outcomes         │
│                                                     │
│  Pre-Award Phase:               11 activities       │
│  Supply Projects:                6 phases           │
│  O&M Services:                   6 phases (+loop)   │
│                                                     │
│  Participants:                   4 actors           │
│  Message Flows:                 11 exchanges        │
│                                                     │
│  Average Duration:                                  │
│    - Pre-Award:                  2-8 weeks          │
│    - Supply Project:             3-12 months        │
│    - O&M Service:                6-36 months        │
│                                                     │
│  Compliance:                     100% ICS           │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Integration Points

### External System Interactions

```
┌──────────────┐         ┌──────────────┐
│   COMPANY    │         │   VENDORS    │
│  (Internal)  │         │ (Suppliers)  │
└──────┬───────┘         └───────┬──────┘
       │                         │
       │ ⇢⇢⇢ RFQ Request ⇢⇢⇢     │
       │                         │
       │ ⇠⇠⇠ Quotations ⇠⇠⇠      │
       │                         │
       │ ⇢⇢⇢ Purchase Order ⇢⇢⇢  │
       │                         │
       │ ⇠⇠⇠ Delivery ⇠⇠⇠        │
       │                         │
       ↓                         ↓

┌──────────────┐         ┌──────────────┐
│   CUSTOMER   │         │    ETIMAD    │
│ (Government) │         │  (Platform)  │
└──────┬───────┘         └───────┬──────┘
       │                         │
       │ ⇠⇠⇠ Submission ⇠⇠⇠      │
       │                         │
       │ ⇢⇢⇢ Decision ⇢⇢⇢        │
       │                         │
       │ ⇢⇢⇢ Award Letter ⇢⇢⇢    │
       │                         │
       │ ⇠⇠⇠ Invoice ⇠⇠⇠         │
       │                         │
       │ ⇢⇢⇢ Payment ⇢⇢⇢         │
       ↓                         ↓
```

---

## 🎓 How to Read This Diagram

### Step-by-Step Guide

1. **Start at the Top**: Begin with ⭕ START
2. **Follow the Arrows**: ↓ shows flow direction
3. **Read Task Boxes**: Each box is an activity
4. **Watch for Diamonds**: ◇ indicates decisions
5. **Check Message Flows**: ⇢⇢⇢ and ⇠⇠⇠ show communications
6. **Track Phases**: Bold boxes (┏━━━┓) group related activities
7. **Find the End**: ⭕ END shows completion

### Example Walkthrough

**Scenario**: Supply Project

1. START → Opportunity Identified
2. Register Tender (Draft)
3. Technical Study → Create BoQ
4. Financial Study → Prepare RFQ
5. Send RFQ → Vendors respond
6. Compare & Select Vendors
7. Prepare Quotation
8. Submit to Customer
9. Customer Evaluates
10. DECISION: Won!
11. PROJECT TYPE: Supply
12. Execute 6 Supply Phases
13. Complete Project → END

**Total Time**: ~6 months average

---

## 📞 Support

### Using These Diagrams

**For Training**:
- Print this document
- Walk through each flow
- Use in presentations
- Training materials

**For Documentation**:
- Reference in manuals
- Show to stakeholders
- Process documentation
- Compliance proof

**For Implementation**:
- Guide development
- Define workflows
- Test scenarios
- Validate processes

---

## ✅ Quick Reference

### Main Paths

```
PATH 1: Supply Project
├─ Pre-Award (2-8 weeks)
├─ Supply Phase 1-6 (3-12 months)
└─ Complete

PATH 2: O&M Service
├─ Pre-Award (2-8 weeks)
├─ O&M Phase 1-6 (6-36 months, with monthly loop)
└─ Complete

PATH 3: Lost/Cancelled
├─ Pre-Award (2-8 weeks)
├─ Document Loss/Cancellation
└─ Archive
```

---

**Visual BPMN Diagram**
**ICS Tender Management v18.0.2.0.0**
**iCloud Solutions**

*Easy-to-Read Process Visualization* 📊
