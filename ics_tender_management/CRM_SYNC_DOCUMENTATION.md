# CRM Synchronization & Tender Control - Complete Guide

## Overview
When opportunities are created from Etimad tenders or linked to active tenders, they become **READ-ONLY in CRM** and automatically synchronize with tender progress. This prevents data conflicts and maintains a single source of truth.

---

## 🎯 Core Principles

### **1. Single Source of Truth**
```
Etimad Tender → Tender (MASTER) → CRM Opportunity (SLAVE)
                   ↓
              All changes happen here
```

### **2. Automatic Synchronization**
When tender state changes, CRM opportunity automatically updates:
- ✅ Stage
- ✅ Probability  
- ✅ Notes (chatter log)

### **3. CRM Protection**
Opportunities linked to active tenders **cannot be edited** in CRM to prevent conflicts.

---

## 📊 Stage Mapping Table

| Tender State | CRM Stage | Probability | Notes |
|-------------|-----------|-------------|-------|
| **Draft** | New | 5% | Initial qualification |
| **Technical** | Qualified | 20% | Technical study in progress |
| **Financial** | Proposition | 40% | Financial analysis |
| **Quotation** | Proposition | 60% | Quotation prepared |
| **Submitted** | Proposition | 75% | Submitted to customer |
| **Evaluation** | Negotiation | 85% | Under customer evaluation |
| **Won** | Won | 100% | Tender won! |
| **Lost** | Lost | 0% | Tender lost |
| **Cancelled** | Lost | 0% | Tender cancelled |

---

## 🔒 Protected Fields (When Linked to Tender)

The following CRM fields become **read-only** when opportunity is linked to active tender:

1. **Stage** - Controlled by tender state
2. **Probability** - Auto-calculated from tender progress
3. **Expected Revenue** - Synced from tender
4. **Deadline** - Synced from tender submission deadline

---

## 🎨 Visual Indicators

### **In CRM Opportunity Form:**

When opening an opportunity linked to a tender:

```
┌────────────────────────────────────────────────────────┐
│ ⚠️ WARNING BANNER (Yellow)                             │
│                                                         │
│ 🔒 This opportunity is controlled by Tender Management │
│                                                         │
│ This opportunity is linked to an active tender and     │
│ cannot be edited directly. All changes must be made    │
│ through the tender form to maintain data consistency.  │
│                                                         │
│ Linked Tender: [TENDER-2024-001] (clickable link)     │
└────────────────────────────────────────────────────────┘
```

### **Visual Cues:**
- 🔒 Lock icon in warning banner
- 🎯 Tender management icon
- Yellow warning background
- Clickable link to tender
- Read-only badges on protected fields

---

## 🚫 Error Prevention

### **Scenario: User Tries to Edit CRM Opportunity**

```python
# User changes stage in CRM
Error Message:
┌────────────────────────────────────────────┐
│ ❌ Cannot Edit Opportunity                 │
│                                             │
│ This opportunity is controlled by Tender   │
│ Management.                                 │
│                                             │
│ Linked Tender: TENDER-2024-001            │
│ Current State: Financial Study             │
│                                             │
│ To modify this opportunity, please update  │
│ the tender instead.                        │
│                                             │
│ Changes to the tender will automatically   │
│ sync to this opportunity.                  │
└────────────────────────────────────────────┘
```

**Blocked Actions:**
- Changing stage manually
- Modifying probability
- Updating expected revenue
- Changing deadline

**Allowed Actions:**
- Adding notes/comments
- Attaching documents
- Viewing history
- Following/subscribing

---

## ⚙️ How It Works

### **1. Opportunity Creation from Etimad**

```python
# When user clicks "Create Opportunity" in Etimad tender
1. Opportunity created with etimad_tender_id link
2. Field is_from_etimad = True
3. Opportunity marked as Etimad-controlled
```

### **2. Tender Creation from CRM**

```python
# When user clicks "Create Tender" in CRM opportunity
1. Tender created with lead_id link
2. Tender becomes master record
3. Opportunity marked as tender-controlled
```

### **3. Automatic Sync Trigger**

```python
# In ics.tender model:
def write(self, vals):
    if vals.get('state'):  # Tender state changed
        for tender in self:
            if tender.lead_id:  # Has linked CRM opportunity
                tender._sync_crm_stage()  # Sync!
```

### **4. Stage Synchronization**

```python
def _sync_crm_stage(self):
    1. Get tender state
    2. Map to CRM stage name
    3. Find CRM stage record
    4. Update opportunity (bypass lock with context)
    5. Log sync in chatter
```

### **5. Protection Mechanism**

```python
# In crm.lead model:
def write(self, vals):
    if 'stage_id' in vals:  # Trying to change stage
        if self.active_tender_id:  # Has active tender
            if not context.get('from_tender_sync'):  # Not from sync
                raise UserError()  # Block it!
```

---

## 📝 Chatter Logs

Every sync is logged in CRM opportunity chatter:

```
┌────────────────────────────────────────────┐
│ 🎯 Tender Stage Update                     │
│                                             │
│ Stage synchronized from Tender:            │
│ [TENDER-2024-001]                          │
│                                             │
│ Tender State: Financial Study              │
│ CRM Stage: Proposition                     │
│ Probability: 40%                           │
│                                             │
│ 2 hours ago by System                      │
└────────────────────────────────────────────┘
```

---

## 🔄 Workflow Examples

### **Example 1: Etimad → Tender → Won**

```
Day 1:
- Etimad scraper finds new tender
- User clicks "Create Opportunity" in Etimad
- CRM opportunity created (Stage: New, 5%)

Day 3:
- User reviews in Tender Management
- Changes tender state to "Technical"
- ✅ CRM syncs: Stage → Qualified, Probability → 20%

Day 7:
- Technical study complete
- Changes tender state to "Financial"
- ✅ CRM syncs: Stage → Proposition, Probability → 40%

Day 10:
- Quotation prepared
- Changes tender state to "Quotation"
- ✅ CRM syncs: Probability → 60%

Day 12:
- Tender submitted to customer
- Changes tender state to "Submitted"
- ✅ CRM syncs: Probability → 75%

Day 15:
- Customer evaluates offers
- Changes tender state to "Evaluation"
- ✅ CRM syncs: Stage → Negotiation, Probability → 85%

Day 20:
- We win the tender!
- Changes tender state to "Won"
- ✅ CRM syncs: Stage → Won, Probability → 100%
- ✅ Project auto-created with tasks!
```

### **Example 2: Direct Tender Creation (Skip CRM)**

```
Day 1:
- Etimad scraper finds tender
- User clicks "🎯 Create Tender Directly"
- Tender created (NO CRM opportunity)
- Work proceeds in Tender Management only
```

### **Example 3: User Tries to Edit CRM**

```
User opens CRM opportunity
Sees: 🔒 Warning banner
Tries to: Change stage to "Won"
Result: ❌ Error message
Action: Opens tender form via link
Updates: Tender state to "Won"
Result: ✅ CRM syncs automatically
```

---

## 🛡️ Benefits

### **1. Data Integrity**
- ✅ Single source of truth (tender)
- ✅ No conflicting updates
- ✅ Consistent reporting

### **2. Workflow Clarity**
- ✅ Clear process: work in Tender Management
- ✅ CRM becomes view-only for tender opportunities
- ✅ Prevents user confusion

### **3. Automatic Updates**
- ✅ Zero manual syncing
- ✅ Real-time reflection
- ✅ Complete audit trail

### **4. Error Prevention**
- ✅ Cannot accidentally change CRM
- ✅ Clear error messages
- ✅ Guided to correct action

---

## 🌍 Bilingual Support

All messages available in:
- ✅ English
- ✅ Arabic (العربية)

**Example Arabic Message:**
```
هذه الفرصة يتم التحكم فيها من خلال إدارة المنافسات.

المنافسة المرتبطة: TENDER-2024-001
الحالة الحالية: الدراسة المالية

لتعديل هذه الفرصة، يرجى تحديث المنافسة بدلاً من ذلك.
سيتم مزامنة التغييرات على المنافسة تلقائيًا مع هذه الفرصة.
```

---

## 🔧 Technical Details

### **New Fields in crm.lead:**

```python
is_from_etimad = fields.Boolean(
    'Created from Etimad',
    compute='_compute_is_from_etimad',
    store=True
)

active_tender_id = fields.Many2one(
    'ics.tender',
    'Active Tender',
    compute='_compute_active_tender',
    store=True
)
```

### **Override Methods:**

```python
# In crm.lead:
def write(self, vals):
    # Block protected field changes when controlled by tender
    # Context 'from_tender_sync' bypasses the lock

# In ics.tender:
def write(self, vals):
    # Trigger _sync_crm_stage() when state changes
```

### **Sync Methods:**

```python
def _sync_crm_stage(self):
    # Map tender state to CRM stage
    # Update opportunity with bypass context
    # Log sync in chatter

def _get_crm_stage_mapping(self):
    # Return state → stage name mapping

def _get_crm_probability(self):
    # Return state → probability mapping
```

---

## 📋 Configuration

### **No Configuration Required!**

The sync works automatically once:
- ✅ ics_tender_management module installed
- ✅ ics_etimad_tenders_crm module installed  
- ✅ CRM module active

### **CRM Stages Required:**

The system looks for these CRM stages:
- New (or Qualification)
- Qualified
- Proposition
- Negotiation
- Won
- Lost

**If stages don't exist:** The sync will try partial matching. Create missing stages for optimal results.

---

## 🚀 Best Practices

### **1. Use Tender Management for All Updates**
```
✅ DO: Update tender state in Tender Management
❌ DON'T: Try to change CRM stages for tender opportunities
```

### **2. Let CRM Be Read-Only**
```
✅ DO: Use CRM for viewing and reporting
❌ DON'T: Fight the protection mechanism
```

### **3. Follow the Guided Workflow**
```
✅ DO: Click linked tender in warning banner
❌ DON'T: Force edits with technical workarounds
```

### **4. Use Direct Flow When Possible**
```
✅ DO: Click "🎯 Create Tender Directly" from Etimad
❌ DON'T: Create unnecessary CRM opportunities
```

---

## 🐛 Troubleshooting

### **Issue: CRM stage not syncing**

**Solution:**
1. Check CRM stages exist (match names in mapping)
2. Verify opportunity has `active_tender_id` set
3. Check tender has `lead_id` set
4. Review chatter logs for errors

### **Issue: Can't edit CRM opportunity**

**Solution:**
This is **CORRECT BEHAVIOR!** 
- Open linked tender via banner link
- Make changes in tender
- CRM will sync automatically

### **Issue: Wrong CRM stage**

**Solution:**
- Check stage mapping in `_get_crm_stage_mapping()`
- Ensure CRM stages match expected names
- Create missing stages in CRM

---

## 📊 Reporting Impact

### **CRM Reports Now Show:**
- ✅ Accurate tender pipeline
- ✅ Real-time probability updates
- ✅ Correct stage distribution
- ✅ Etimad-sourced opportunities marked
- ✅ Win/loss rates from actual tender outcomes

### **No More:**
- ❌ Stale CRM data
- ❌ Manual stage updates
- ❌ Conflicting information
- ❌ Lost opportunities in CRM

---

## ✅ Summary

| Feature | Status |
|---------|--------|
| **Automatic sync** | ✅ Active |
| **CRM protection** | ✅ Active |
| **Stage mapping** | ✅ 9 states mapped |
| **Probability calc** | ✅ Automatic |
| **Visual warnings** | ✅ Banner + readonly |
| **Error messages** | ✅ Bilingual |
| **Chatter logging** | ✅ Every sync |
| **Backward compatible** | ✅ Yes |

---

**Version:** 18.0.2.1.0  
**Last Updated:** 2026-01-30  
**Commit:** b8e64e0

**Recommendation:** Use Tender Management as your primary workflow. CRM becomes a powerful reporting dashboard that stays perfectly synchronized! 🎯
