# Dates Section Validation - Tender 2026/20

## Screenshot Analysis

The user provided a screenshot showing the **"العناوين والمواعيد المتعلقة بالمنافسة"** (Dates and Deadlines) section from Etimad.

---

## Fields Present in Screenshot

| # | Etimad Field (Arabic) | Etimad Field (English) | Value in Tender 2026/20 | Model Field | Status |
|---|---------------------|----------------------|----------------------|-------------|---------|
| 1 | آخر موعد لإستلام الإستفسارات | Last date to receive inquiries | 06/02/2026 (18/08/1447) | `last_enquiry_date` | [OK] Captured |
| 2 | آخر موعد لتقديم العروض | Last date to submit offers | 19/02/2026 09:59 AM (02/09/1447) | `offers_deadline` | [OK] Captured |
| 3 | تاريخ فتح العروض | Offer opening date | 19/02/2026 10:00 AM (02/09/1447) | `offer_opening_date` | [OK] Captured |
| 4 | تاريخ فحص العروض | Offer examination date | لا يوجد (Not available) | `offer_examination_date` | [OK] Captured |
| 5 | **فترة التوقيف** | **Suspension period** | **5** | [!] **MISSING** | [!] **Not captured** |
| 6 | التاريخ المتوقع للترسية | Expected award date | 25/02/2026 (08/09/1447) | `expected_award_date` | [OK] Captured |
| 7 | تاريخ بدء الأعمال / الخدمات | Work/services start date | 04/03/2026 (15/09/1447) | `work_start_date` | [OK] Captured |
| 8 | بداية إرسال الأسئلة و الإستفسارات | Start of sending questions | 03/02/2026 (15/08/1447) | `inquiry_start_date` | [OK] Captured |
| 9 | اقصى مدة للاجابة على الإستفسارات | Max duration to answer inquiries | 10 (days) | `max_inquiry_response_days` | [OK] Captured |
| 10 | مكان فتح العروض | Place of opening offers | بلدية محافظة المزاحمية | `opening_location` | [OK] Captured |

---

## Missing Field: Suspension Period (فترة التوقيف)

### What is Suspension Period?

**Arabic:** فترة التوقيف  
**English:** Suspension Period  
**Value in 2026/20:** 5 (days)

### What Does It Mean?

The suspension period (also called "standstill period" or "waiting period") is a mandatory waiting period **after** the tender closes and **before** the contract can be awarded. 

**Purpose:**
- Allows time for potential challenges/complaints
- Gives losing bidders time to review award decision
- Ensures transparency and fairness
- Required by Saudi procurement regulations

**In Tender 2026/20:**
- Offers close: 19/02/2026
- Suspension period: **5 days**
- Expected award: 25/02/2026 (19 + 5 = 24, but +1 for weekend = 25)

### Why It Matters

**For Bidders:**
- Know when award decision will be final
- Plan for potential challenge period
- Timeline for contract finalization

**For Contracting:**
- Critical for project timeline planning
- Affects start date calculation
- Required for compliance

### Implementation Needed

**Add Field:**
```python
suspension_period_days = fields.Integer("Suspension Period (Days)", 
    help="فترة التوقيف - Mandatory waiting period before contract award")
```

**Parser Update:**
Add to `_parse_dates_html()` method:
```python
# Extract suspension period
suspension_elements = tree.xpath('//div[contains(text(), "فترة التوقيف")]/following-sibling::div[1]//span/text()')
if suspension_elements:
    try:
        parsed_data['suspension_period_days'] = int(suspension_elements[0].strip())
    except ValueError:
        pass
```

**View Update:**
Add to "Dates & Deadlines" tab:
```xml
<field name="suspension_period_days" string="Suspension Period (Days)"/>
```

---

## Complete Date Fields Inventory

### [OK] Currently Captured (9 date fields)

1. `last_enquiry_date` (Datetime) - Last date for questions
2. `offers_deadline` (Datetime) - Submission deadline (with time)
3. `offer_opening_date` (Datetime) - When offers are opened
4. `offer_examination_date` (Datetime) - When offers are examined
5. `expected_award_date` (Date) - Expected award date
6. `work_start_date` (Date) - Contract start date
7. `inquiry_start_date` (Date) - When questions can start
8. `max_inquiry_response_days` (Integer) - Days to answer questions
9. `opening_location` (Char) - Physical location for opening

### [!] Missing (1 field)

1. `suspension_period_days` (Integer) - **Suspension/standstill period**

---

## Date Flow Timeline for Tender 2026/20

```
03/02/2026 ← inquiry_start_date
    ↓ (Questions period starts)
    
06/02/2026 ← last_enquiry_date (10 days response time)
    ↓ (Last day for questions)
    
19/02/2026 09:59 AM ← offers_deadline
    ↓ (Submission closes)
    
19/02/2026 10:00 AM ← offer_opening_date
    ↓ (Offers opened, 1 minute after deadline)
    
لا يوجد ← offer_examination_date
    ↓ (No specific exam date)
    
[5 days suspension period] [!] Missing field
    ↓
    
25/02/2026 ← expected_award_date
    ↓ (Award decision)
    
04/03/2026 ← work_start_date
    ↓ (Contract work begins)
```

---

## Data Source

**API Endpoint:** `GetTenderDatesViewComponenet`  
**URL:** `https://tenders.etimad.sa/Tender/GetTenderDatesViewComponenet?tenderIdStr={id}`

**HTML Structure:**
```html
<div class="etd-item-title">فترة التوقيف</div>
<div><span>5</span></div>
```

---

## Business Impact

### High Priority [!]

The suspension period is **critical for timeline planning**:

**Scenario Without This Field:**
- User sees: Expected award = 25/02/2026
- User doesn't know: There's a 5-day waiting period
- Problem: Can't understand why there's a gap between closing (19th) and award (25th)
- Impact: Incorrect timeline expectations

**Scenario With This Field:**
- User sees: Closing date = 19/02/2026
- User sees: Suspension period = 5 days
- User sees: Expected award = 25/02/2026
- User understands: 19 + 5 days suspension + 1 day (weekend) = 25
- Benefit: Clear, compliant timeline

### Use Cases

1. **Project Planning:** Calculate realistic start dates
2. **Challenge Period:** Know when objections can be filed
3. **Resource Allocation:** Plan team availability
4. **Compliance:** Understand procurement regulations
5. **Cash Flow:** Plan for delayed award

---

## Recommendation

### Priority: Medium

While not blocking for basic functionality, this field:
- [OK] Is displayed prominently in Etimad UI
- [OK] Affects timeline understanding
- [OK] Required for compliance awareness
- [OK] Easy to implement (same pattern as other fields)

**Recommendation:** Add in next update

---

## Implementation Estimate

**Effort:** Low (15 minutes)

1. Add field to model (1 line)
2. Update parser (5 lines)
3. Update form view (1 line)
4. Test with tender 2026/20

**Files to Modify:**
- `ics_etimad_tenders_crm/models/etimad_tender.py`
- `ics_etimad_tenders_crm/views/etimad_tender_views.xml`

**No Breaking Changes:** New field, existing data unaffected

---

## Testing Checklist

After implementation:

- [ ] Open tender 2026/20
- [ ] Click "Fetch Details"
- [ ] Go to "Dates & Deadlines" tab
- [ ] Verify shows: **Suspension Period: 5 days**
- [ ] Verify timeline makes sense:
  - Closing: 19/02
  - + 5 days suspension
  - = Award: 25/02 ✓

---

## Summary

**Current Status:** 9 out of 10 date fields captured [OK]  
**Missing:** 1 field (Suspension Period) [!]  
**Impact:** Medium (affects timeline understanding)  
**Implementation:** Easy (same pattern as existing fields)  

**Recommendation:** Add `suspension_period_days` field to complete date coverage

---

**Validated:** 2026-02-03  
**Tender Sample:** 2026/20 (Riyadh Municipality)  
**Screenshot:** Dates & Deadlines tab from Etimad portal
