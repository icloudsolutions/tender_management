# Automated Activities & Appeal Workflow - Complete Guide

## Overview
The system now automatically creates **activity tasks** for each tender phase, ensuring nothing is missed. When a tender is lost, users are guided through the **appeal process (حق الإعتراض)** with complete tracking.

---

## 🎯 Automated Activities by Phase

### **Phase 1: Draft / Qualification (مرحلة التأهيل)**

#### **Activity 1: Download Tender Documents from Etimad** 📥
**Triggered:** When tender enters 'draft' state  
**Priority:** High  
**Deadline:** Today

**Tasks:**
1. ✅ Login to your Etimad account
2. ✅ Download ALL tender documents
3. ✅ Review technical specifications
4. ✅ Attach documents to this tender

**Arabic:** "📥 تحميل مستندات المنافسة من إعتماد"

#### **Activity 2: Schedule Site Visit** 📍 (IF REQUIRED)
**Triggered:** When `site_visit_required = True`  
**Type:** Meeting  
**Deadline:** Last inquiry date

**Tasks:**
1. ✅ Coordinate site visit date with customer
2. ✅ Prepare required documents for site
3. ✅ Assign team members for visit
4. ✅ Update site visit date in tender form

**Arabic:** "📍 جدولة الزيارة الميدانية"

---

### **Phase 2: Technical Study (الدراسة الفنية)**

#### **Activity: Complete Technical Study & BoQ** 📋
**Triggered:** When tender state → 'technical'  
**Priority:** High  
**Deadline:** Today

**Tasks:**
1. ✅ Review technical specifications
2. ✅ Import/create Bill of Quantities
3. ✅ Define product requirements
4. ✅ Identify potential vendors
5. ✅ Estimate quantities and costs

**Arabic:** "📋 إكمال الدراسة الفنية وجدول الكميات"

---

### **Phase 3: Financial Study (الدراسة المالية)**

#### **Activity: Request Vendor Quotations** 💰
**Triggered:** When tender state → 'financial'  
**Priority:** High  
**Deadline:** Today

**Tasks:**
1. ✅ Send RFQs to selected vendors
2. ✅ Collect and review vendor offers
3. ✅ Compare vendor prices
4. ✅ Select best vendors per product
5. ✅ Calculate final margin

**Arabic:** "💰 طلب عروض أسعار الموردين"

---

### **Phase 4: Quotation Prepared (تم إعداد عرض السعر)**

#### **Activity: Review & Approve Quotation** 📄
**Triggered:** When tender state → 'quotation'  
**Priority:** High  
**Deadline:** Submission deadline

**Tasks:**
1. ✅ Review generated quotation
2. ✅ Verify prices and margins
3. ✅ Get internal approvals (Direct/Dept/Financial/CEO)
4. ✅ Prepare submission documents
5. ✅ Final quality check

**Arabic:** "📄 مراجعة واعتماد عرض السعر"

---

### **Phase 5: Submitted (تم التقديم)**

#### **Activity: Confirm Submission & Track** ✅
**Triggered:** When tender state → 'submitted'  
**Priority:** Normal  
**Deadline:** Opening date

**Tasks:**
1. ✅ Confirm submission receipt from customer
2. ✅ Monitor tender evaluation timeline
3. ✅ Prepare for clarification questions
4. ✅ Track opening date

**Arabic:** "✅ تأكيد التقديم والمتابعة"

---

### **Phase 6: Under Evaluation (قيد التقييم)**

#### **Activity: Monitor Evaluation & Prepare Response** 🔍
**Triggered:** When tender state → 'evaluation'  
**Priority:** High  
**Deadline:** Today

**Tasks:**
1. ✅ Monitor customer evaluation progress
2. ✅ Respond to clarification requests
3. ✅ Prepare for negotiations if needed
4. ✅ Track competitor information
5. ✅ Stay ready for final presentations

**Arabic:** "🔍 متابعة التقييم وإعداد الردود"

---

## ⚖️ Appeal Workflow (حق الإعتراض)

### **When Tender is Lost**

**IMPORTANT:** Saudi regulations give you **the right to appeal** tender results!

#### **Automatic Activity Created:** ⚖️
**Title:** "Consider Appeal (إعتراض) - You Have the Right!"  
**Priority:** HIGH  
**Deadline:** Today (appeals are time-sensitive!)

### **Activity Content (Bilingual):**

```
🔴 حق الإعتراض متاح:
الشركة لها الحق في تقديم إعتراض على نتيجة المنافسة.

الخطوات المطلوبة:
1. إعداد خطاب الإعتراض: قم بإعداد خطاب رسمي يوضح أسباب الإعتراض
2. إرسال الإعتراض: قدم الخطاب للجهة المعنية عبر القنوات الرسمية
3. إنتظار الرد: راقب استجابة الجهة الحكومية
4. المتابعة: هناك إمكانية أن يتم قبول الطلب

⏰ Act quickly - appeals are usually time-sensitive!
```

---

## 📝 Appeal Process Steps

### **Step 1: Submit Appeal**

Go to **"Offer Results"** tab in tender form:

```
┌─────────────────────────────────────────────────┐
│ 💡 حق الإعتراض متاح                            │
│                                                  │
│ لديك الحق في تقديم إعتراض على نتيجة المنافسة.  │
│ قد يتم قبول الإعتراض إذا كانت الأسباب وجيهة.   │
│                                                  │
│ You have the right to appeal.                   │
│ Click the checkbox to start the appeal process. │
└─────────────────────────────────────────────────┘

Appeal Workflow:
├─ ☑ Appeal Submitted
├─ 📅 Appeal Submission Date: [Select Date]
├─ 📎 Appeal Letter: [Upload File]
└─ 📝 Appeal Reason: [Explain why you disagree]
```

### **Step 2: Track Response**

```
Appeal Status: 🟡 Pending Response
├─ 📅 Appeal Response Date: [When received]
└─ 📝 Appeal Response Notes: [Response details]
```

### **Step 3: Possible Outcomes**

| Status | Color | Meaning | Next Action |
|--------|-------|---------|-------------|
| 🟡 **Pending** | Yellow | Awaiting response | Monitor and follow up |
| 🟢 **Accepted** | Green | Appeal successful! | May change tender to Won |
| 🔴 **Rejected** | Red | Appeal denied | Close tender |
| ⚪ **Withdrawn** | Gray | Appeal cancelled | No further action |

---

## 🎨 Visual Experience

### **Activities Panel (Top Right):**

```
┌─────────────────────────────────────────┐
│ 📥 Activities                     🔔 6  │
├─────────────────────────────────────────┤
│ 📥 Download Tender Documents            │
│    Due: Today | Assigned: You           │
│    ├─ Login to Etimad                   │
│    ├─ Download all docs                 │
│    └─ Attach to tender                  │
├─────────────────────────────────────────┤
│ 📍 Schedule Site Visit                  │
│    Due: 2024-02-10 | Meeting            │
│    ├─ Coordinate with customer          │
│    └─ Prepare documents                 │
├─────────────────────────────────────────┤
│ 📋 Complete Technical Study             │
│    Due: Today | Priority: High          │
│    ├─ Create BoQ                        │
│    └─ Identify vendors                  │
└─────────────────────────────────────────┘
```

### **Appeal Banner (When Lost):**

```
┌─────────────────────────────────────────────────┐
│ 💡 حق الإعتراض متاح                            │
│                                                  │
│ لديك الحق في تقديم إعتراض على نتيجة المنافسة.  │
│ قد يتم قبول الإعتراض إذا كانت الأسباب وجيهة.   │
│                                                  │
│ You have the right to appeal.                   │
│ Click the checkbox above to start.              │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Activity Automation Flow

### **Trigger Mechanism:**

```python
# When tender state changes
tender.state = 'technical'  # User action
     ↓
write() method called
     ↓
_trigger_state_activities()
     ↓
_activity_technical_study()
     ↓
Activity created automatically! ✅
     ↓
User sees activity in panel
```

### **Smart Scheduling:**

```python
Activity Deadlines:
- Draft: Today (urgent - download docs)
- Technical: Today (start BoQ work)
- Financial: Today (send RFQs)
- Quotation: Submission deadline (time-sensitive)
- Submitted: Opening date (track result)
- Evaluation: Today (respond quickly)
- Lost: Today (appeal deadline approaching!)
```

---

## 📊 Complete Activity Timeline Example

```
Day 1: Tender Created (Draft)
├─ 📥 Activity: Download Etimad docs (Due: Today)
└─ 📍 Activity: Schedule site visit (Due: Feb 10)

Day 3: State → Technical
├─ ✅ Completed: Downloaded docs
├─ ✅ Completed: Site visit scheduled
└─ 📋 NEW Activity: Complete BoQ (Due: Today)

Day 7: State → Financial  
├─ ✅ Completed: BoQ ready
└─ 💰 NEW Activity: Request vendor quotes (Due: Today)

Day 10: State → Quotation
├─ ✅ Completed: Vendors responded
└─ 📄 NEW Activity: Review quotation (Due: Feb 20)

Day 15: State → Submitted
├─ ✅ Completed: Quotation approved
└─ ✅ NEW Activity: Confirm submission (Due: Feb 25)

Day 20: State → Evaluation
└─ 🔍 NEW Activity: Monitor evaluation (Due: Today)

Day 25: State → Lost 😞
└─ ⚖️ NEW Activity: Consider Appeal! (Due: TODAY!)
```

---

## ⚖️ Appeal Workflow Details

### **New Fields Added:**

| Field | Type | Description |
|-------|------|-------------|
| `appeal_submission_date` | Date | When appeal was submitted |
| `appeal_letter_file` | Binary | Upload appeal letter PDF |
| `appeal_reason` | Text | Detailed reason for appeal |
| `appeal_status` | Selection | Pending/Accepted/Rejected/Withdrawn |
| `appeal_response_date` | Date | When customer responded |
| `appeal_response_notes` | Text | Response details |

### **Appeal Status Flow:**

```
Tender Lost
    ↓
☑ Check "Appeal Submitted"
    ↓
Fill appeal details:
  - Upload letter
  - Explain reason  
  - Set submission date
    ↓
Status: 🟡 Pending Response
    ↓
Wait for customer response...
    ↓
Update response:
  - Response date
  - Response notes
  - Final status
    ↓
Outcome:
  ├─ 🟢 Accepted → May win tender
  ├─ 🔴 Rejected → Confirm loss
  └─ ⚪ Withdrawn → Case closed
```

---

## 🎨 UI Enhancements in Tender Form

### **"Offer Results" Tab - NEW Section:**

```
╔════════════════════════════════════════════╗
║  Appeal Workflow (حق الإعتراض)             ║
╠════════════════════════════════════════════╣
║                                             ║
║  ☑ Appeal Submitted                        ║
║  📅 Appeal Submission Date: 2024-02-15     ║
║  📎 Appeal Letter: [Upload PDF]            ║
║  📝 Appeal Reason: [Explain]               ║
║                                             ║
║  Appeal Status: 🟡 Pending Response        ║
║  📅 Response Date: [Not yet received]      ║
║  📝 Response Notes: [Waiting...]           ║
╚════════════════════════════════════════════╝

┌────────────────────────────────────────────┐
│ 💡 حق الإعتراض متاح                        │
│                                             │
│ لديك الحق في تقديم إعتراض على نتيجة       │
│ المنافسة. قد يتم قبول الإعتراض إذا كانت   │
│ الأسباب وجيهة.                             │
│                                             │
│ You have the right to appeal.              │
│ Click the checkbox above to start.         │
└────────────────────────────────────────────┘
```

---

## 📋 Activity Details

### **Activity Types Used:**

| Icon | Type | Usage |
|------|------|-------|
| 📥 | To-do | Document download, reviews |
| 📍 | Meeting | Site visits, presentations |
| 💰 | To-do | Financial tasks |
| ⚖️ | To-do | Appeal process |

### **Activity Structure:**

```python
{
    'summary': 'Task title (bilingual)',
    'note': 'Detailed HTML instructions',
    'user_id': tender.user_id,  # Assigned to tender owner
    'date_deadline': calculated_date,
    'activity_type_id': mail.mail_activity_data_todo
}
```

---

## 🌍 Bilingual Support

Every activity is **fully bilingual**:

**Example:**
```
Title: 📥 Download Tender Documents from Etimad
       📥 تحميل مستندات المنافسة من إعتماد

Content:
Action Required:
- Login to your Etimad account
- Download all tender documents
- Review technical specifications
- Attach documents to this tender

إجراء مطلوب:
- تسجيل الدخول إلى حساب إعتماد
- تحميل جميع مستندات المنافسة
- مراجعة المواصفات الفنية
- إرفاق المستندات
```

---

## ⚖️ Appeal Rights (حق الإعتراض)

### **Legal Context:**

Per Saudi government procurement regulations:
- ✅ Companies have the **legal right to appeal** tender results
- ✅ Appeals must be submitted with valid justification
- ✅ Government agencies **must review** appeals
- ✅ There is a **possibility** the appeal will be accepted (في إمكانية أن الطلب يتقبل)

### **When to Appeal:**

**Valid Reasons:**
- ❌ Evaluation criteria not followed
- ❌ Technical specifications misinterpreted
- ❌ Financial calculations incorrect
- ❌ Procedural violations occurred
- ❌ Unjustified disqualification

### **Appeal Process:**

```
1️⃣ PREPARE
├─ Draft formal appeal letter (Arabic)
├─ Gather supporting evidence
├─ Reference specific tender clauses
└─ Explain technical/financial justification

2️⃣ SUBMIT
├─ Upload letter to tender form
├─ Enter detailed reason
├─ Mark submission date
└─ Set status: "Pending Response"

3️⃣ TRACK
├─ Monitor response timeline
├─ Follow up if delayed
├─ Document all communications
└─ Update response details

4️⃣ OUTCOME
├─ Accepted → Tender may become "Won"!
├─ Rejected → Document reasons, close
└─ Withdrawn → Internal decision to withdraw
```

---

## 🎯 Use Cases

### **Use Case 1: Site Visit Required**

```
Scenario:
- Tender requires site visit (checkbox checked)
- System automatically creates meeting activity
- User coordinates with customer
- Site visit scheduled
- Documents prepared
- Visit completed
- Date updated in tender form
- Activity marked done ✅
```

### **Use Case 2: Lost Tender with Appeal**

```
Scenario:
- Tender evaluation complete
- Customer selects competitor
- User marks tender as "Lost"
- ⚖️ Activity created: "Consider Appeal"
- User reviews loss reasons
- Decides to appeal
- Goes to "Offer Results" tab
- Checks "Appeal Submitted"
- Uploads appeal letter
- Enters justification
- Submits to customer
- Waits for response...
- Customer accepts appeal! 🎉
- User changes tender to "Won"
- Project auto-created
- Success! 🚀
```

### **Use Case 3: Etimad Document Management**

```
Scenario:
- New tender from Etimad scraper
- User opens tender
- 📥 Activity appears: "Download docs from Etimad"
- User clicks Etimad link
- Logs into Etimad portal
- Downloads: Technical specs, conditions, BOQ template
- Attaches all files to tender
- Marks activity as done ✅
- Proceeds to technical study
```

---

## ⚙️ Technical Implementation

### **Activity Trigger:**

```python
def write(self, vals):
    old_states = {tender.id: tender.state for tender in self}
    res = super().write(vals)
    
    if vals.get('state'):
        for tender in self:
            old_state = old_states[tender.id]
            if old_state != tender.state:
                # Trigger activities based on new state
                tender._trigger_state_activities(old_state, tender.state)
```

### **Activity Creation:**

```python
def _activity_draft_qualification(self):
    self.activity_schedule(
        'mail.mail_activity_data_todo',
        summary=_('📥 Download Tender Documents'),
        note=_('<strong>Tasks...</strong>'),
        user_id=self.user_id.id,
        date_deadline=fields.Date.today()
    )
```

### **Appeal Trigger:**

```python
# In write() method
if vals.get('state') == 'lost':
    for tender in self:
        tender._trigger_appeal_option()
```

---

## 📊 Benefits

### **Before (Manual):**
- ❌ Users forget steps
- ❌ No consistency
- ❌ Missing deadlines
- ❌ Lost opportunities
- ❌ No appeal tracking

### **After (Automated):**
- ✅ Every step tracked
- ✅ Consistent process
- ✅ Never miss deadlines
- ✅ Appeal rights preserved
- ✅ Complete audit trail

---

## 🔔 Activity Notifications

Users receive notifications:
- 📧 **Email** - Activity assigned
- 🔔 **Browser** - Activity reminder
- 📱 **Odoo Discuss** - Activity mention
- ⏰ **Calendar** - Meeting activities

---

## 📈 Compliance & Audit

### **Audit Trail:**
Every activity is logged:
- ✅ Who created it (system)
- ✅ When it was due
- ✅ When it was completed
- ✅ Who completed it
- ✅ Any notes added

### **Compliance:**
- ✅ Follows documented procedures
- ✅ Ensures qualification requirements met
- ✅ Tracks appeal rights
- ✅ Documents every phase
- ✅ Saudi procurement compliant

---

## 🎯 Activity Summary Table

| Phase | Activity | Icon | Auto-Created | Deadline |
|-------|----------|------|--------------|----------|
| Draft | Download Etimad Docs | 📥 | ✅ | Today |
| Draft | Schedule Site Visit | 📍 | ✅ (if required) | Inquiry date |
| Technical | Complete BoQ | 📋 | ✅ | Today |
| Financial | Request Vendor Quotes | 💰 | ✅ | Today |
| Quotation | Review & Approve | 📄 | ✅ | Submission date |
| Submitted | Confirm & Track | ✅ | ✅ | Opening date |
| Evaluation | Monitor & Respond | 🔍 | ✅ | Today |
| Lost | Consider Appeal | ⚖️ | ✅ | TODAY! |

**Total:** 8 automated activities across tender lifecycle

---

## 💡 Tips & Best Practices

### **1. Complete Activities Promptly**
```
✅ DO: Mark done when actually completed
❌ DON'T: Ignore activity reminders
```

### **2. Use Activity Notes**
```
✅ DO: Add completion notes for audit trail
❌ DON'T: Just click "Done" without documenting
```

### **3. Appeal Within Deadline**
```
⏰ CRITICAL: Appeals are time-sensitive (usually 3-5 days)
✅ DO: Act immediately when tender is lost
❌ DON'T: Delay - you may lose appeal right
```

### **4. Attach All Documents**
```
✅ DO: Attach Etimad docs when activity reminds you
❌ DON'T: Skip document attachment step
```

---

## 🚀 Future Enhancements (Optional)

- [ ] Configurable activity templates per company
- [ ] Custom activity rules per tender category
- [ ] Automated deadline reminders (email)
- [ ] Activity dependency chains
- [ ] Appeal letter templates
- [ ] Integration with external appeal systems

---

**Status:** ✅ **COMPLETE**  
**Version:** 18.0.2.1.0  
**Commit:** 2531b68  
**Date:** 2026-01-30

**Activities are now FULLY AUTOMATED! Your team will never miss a critical tender step again!** 🎯
