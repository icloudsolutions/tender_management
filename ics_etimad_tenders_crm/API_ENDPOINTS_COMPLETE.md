# Complete Etimad API Endpoints Implementation

## Overview

All 4 Etimad tender detail API endpoints are now fully implemented with robust parsing (lxml + regex fallback).

---

## Implemented Endpoints

### 1. GetRelationsDetailsViewComponenet [OK]

**URL:** `https://tenders.etimad.sa/Tender/GetRelationsDetailsViewComponenet?tenderIdStr={tender_id}`

**Extracts:**
- Classification field (مجال التصنيف)
- Classification required (yes/no)
- Execution location type (داخل/خارج المملكة)
- Execution regions (مناطق التنفيذ)
- Execution cities (مدن التنفيذ)
- Tender purpose/details (التفاصيل)
- Activity details (نشاط المنافسة)
- Supply items included (تشمل بنود توريد)
- Construction works (أعمال الإنشاء)
- Maintenance & operation works (أعمال الصيانة والتشغيل)

**Fields Updated:**
- `classification_field`
- `classification_required`
- `execution_location_type`
- `execution_regions`
- `execution_cities`
- `tender_purpose`
- `activity_details`
- `includes_supply_items`
- `construction_works`
- `maintenance_works`

**Status:** [OK] Complete - Full lxml + regex fallback

---

### 2. GetTenderDatesViewComponenet [OK]

**URL:** `https://tenders.etimad.sa/Tender/GetTenderDatesViewComponenet?tenderIdStr={tender_id}`

**Extracts:**
- Last enquiry date (آخر موعد لإستلام الإستفسارات)
- Offers deadline (آخر موعد لتقديم العروض) - with time
- Offer opening date (تاريخ فتح العروض)
- Offer examination date (تاريخ فحص العروض) - with time
- Expected award date (التاريخ المتوقع للترسية)
- Work start date (تاريخ بدء الأعمال)
- Inquiry start date (بداية إرسال الأسئلة)
- Max inquiry response days (اقصى مدة للاجابة)
- Opening location (مكان فتح العرض)

**Fields Updated:**
- `last_enquiry_date`
- `offers_deadline`
- `offer_opening_date`
- `offer_examination_date`
- `expected_award_date`
- `work_start_date`
- `inquiry_start_date`
- `max_inquiry_response_days`
- `opening_location`

**Status:** [OK] Complete - Full lxml + regex fallback, date/time parsing

---

### 3. GetAwardingResultsForVisitorViewComponenet [OK] (Improved)

**URL:** `https://tenders.etimad.sa/Tender/GetAwardingResultsForVisitorViewComponenet?tenderIdStr={tender_id}`

**Extracts:**
- Award announced (yes/no)
- Award announcement date (تاريخ الإعلان)
- Awarded company name (اسم الشركة المرسية)
- Awarded amount (المبلغ المرسى عليه)

**Fields Updated:**
- `award_announced`
- `award_announcement_date`
- `awarded_company_name`
- `awarded_amount`

**Status:** [OK] Complete - **IMPROVED** with full extraction (was incomplete)

**Improvements Made:**
- Added company name extraction with multiple xpath strategies
- Added awarded amount extraction with number parsing
- Added award date extraction
- Added table-based parsing for alternative HTML structures
- Added comprehensive regex fallback

---

### 4. GetLocalContentDetailsViewComponenet [OK] (NEW)

**URL:** `https://tenders.etimad.sa/Tender/GetLocalContentDetailsViewComponenet?tenderIdStr={tender_id}`

**Extracts:**
- Local content required (yes/no)
- Minimum local content percentage (نسبة المحتوى المحلي الدنيا)
- Calculation mechanism (آلية احتساب المحتوى المحلي)
- Target percentage for evaluation (النسبة المستهدفة للتقييم)
- Weight in tender evaluation (وزن المحتوى المحلي)
- SME participation allowed (مشاركة المنشآت الصغيرة والمتوسطة)
- SME price preference % (الأفضلية السعرية)
- SME qualification mandatory (شهادة المنشآت إلزامية)
- Additional notes

**Fields Added:**
- `local_content_required`
- `local_content_percentage`
- `local_content_mechanism`
- `local_content_target_percentage`
- `local_content_baseline_weight`
- `sme_participation_allowed`
- `sme_price_preference`
- `sme_qualification_mandatory`
- `local_content_notes`

**Status:** [OK] NEW - Full lxml + regex fallback implementation

---

## Usage

### Automatic Fetching

When the system fetches tenders (daily cron or manual fetch), it retrieves basic information. To get complete details including local content:

1. Open any tender record
2. Click **"Fetch Details"** button (in list view) or **"Fetch Detailed Info"** (in form)
3. System fetches from all 4 endpoints
4. All fields updated
5. Notification shows how many endpoints succeeded

### View Local Content

**Form View → Tab 6: "Local Content & SME"**

Shows:
- Local content requirements (if any)
- Minimum percentage required
- Target percentage for evaluation
- Weight in evaluation
- Calculation mechanism
- SME participation details
- SME benefits (price preference, certificate requirements)

**Search Filters:**
- "🇸🇦 Local Content Required" - Filter tenders with local content requirements
- "🏢 SME Allowed" - Filter tenders where SME can participate

---

## Why Local Content Matters

### Saudi Local Content Requirements (المحتوى المحلي)

Saudi Arabia's Vision 2030 includes increasing local content in government procurement:

1. **Mandatory Percentages:** Many tenders require minimum % of local products/services
2. **Evaluation Weight:** Local content % affects your technical score
3. **Compliance:** Must meet minimum to qualify
4. **Competitive Advantage:** Higher local content = better evaluation

### SME Benefits (المنشآت الصغيرة والمتوسطة)

Small & Medium Enterprises get special advantages:

1. **Price Preference:** SME bids get automatic % discount in evaluation (typically 5-10%)
2. **Qualification:** Some tenders require or prefer SME certified companies
3. **Reserved Tenders:** Some tenders are SME-only

**Example:**
- Your bid: 1,000,000 SAR
- SME price preference: 10%
- Evaluated as: 900,000 SAR (10% advantage)

---

## Change Detection

Local content changes are tracked like other critical fields:

**If Etimad updates:**
- Local content percentage increases → Notification + chatter message
- SME participation added → Alert users
- Requirements change → Full change log

---

## Fields Summary

### Local Content Fields (9 new fields)

| Field | Type | Purpose |
|-------|------|---------|
| `local_content_required` | Boolean | Has requirements? |
| `local_content_percentage` | Float | Minimum % required |
| `local_content_target_percentage` | Float | Target for evaluation |
| `local_content_baseline_weight` | Float | Weight in scoring |
| `local_content_mechanism` | Char | Calculation method |
| `sme_participation_allowed` | Boolean | SME can participate? |
| `sme_price_preference` | Float | Price advantage % |
| `sme_qualification_mandatory` | Boolean | Certificate required? |
| `local_content_notes` | Text | Additional notes |

### Award Fields (Enhanced)

| Field | Status | Enhancement |
|-------|--------|-------------|
| `award_announced` | Existing | [OK] Working |
| `award_announcement_date` | Existing | [OK] **NOW EXTRACTED** |
| `awarded_company_name` | Existing | [OK] **NOW EXTRACTED** |
| `awarded_amount` | Existing | [OK] **NOW EXTRACTED** |

---

## Technical Implementation

### Parsing Strategy

**Primary (lxml):**
```python
tree = html.fromstring(html_content)
elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "نسبة المحتوى")]/following-sibling::div[1]//span/text()')
```

**Fallback (regex):**
```python
match = re.search(r'نسبة المحتوى المحلي.*?<span>\s*(\d+(?:\.\d+)?)', html_content, re.DOTALL)
```

**Advantages:**
- Works even if Etimad changes HTML structure slightly
- Robust to missing data (no crashes)
- Logs warnings for debugging
- Returns partial data if some fields fail

### Error Handling

Each endpoint fetch is wrapped in try/except:
- Individual endpoint failure doesn't stop others
- Warning logged for each failure
- Partial data saved (update what succeeded)
- User sees total endpoints fetched: "Fetched from 3/4 endpoints"

---

## Testing Checklist

After deploying, verify:

### Local Content Tab
- [ ] Tab 6 appears in form view
- [ ] Shows "No local content requirements" when `local_content_required = False`
- [ ] Shows all fields when `local_content_required = True`
- [ ] Percentages display correctly
- [ ] SME section appears when `sme_participation_allowed = True`
- [ ] Green alert shows for SME allowed tenders

### Award Results
- [ ] Company name extracts correctly
- [ ] Awarded amount extracts correctly
- [ ] Award date extracts correctly
- [ ] "Not announced yet" shows when no results

### Search Filters
- [ ] "🇸🇦 Local Content Required" filter works
- [ ] "🏢 SME Allowed" filter works
- [ ] Filters combine properly with other filters

### Data Fetching
- [ ] "Fetch Details" button fetches from all 4 endpoints
- [ ] Notification shows "Fetched from 4 endpoint(s)"
- [ ] All fields populate correctly
- [ ] Chatter message posted

---

## Real-World Example

**Tender:** Supply of Medical Equipment

**Local Content Tab Shows:**
```
Local Content Required: [OK] Yes
Minimum Required %: 30%
Target for Evaluation %: 50%
Weight in Evaluation %: 20%
Mechanism: نسبة المكون المحلي حسب شهادة هيئة المحتوى المحلي

SME Participation Allowed: [OK] Yes
SME Price Preference %: 10%
SME Certificate Mandatory: ❌ No
```

**Meaning:**
- You must have at least 30% local content to qualify
- If you achieve 50%+ local content, you get full 20% technical score
- If you're SME certified, your 1M bid counts as 900K (10% advantage)
- SME certificate gives advantage but not required to participate

---

## Future Enhancements

Possible improvements:
- Visual indicator for local content % in list view
- SME badge in kanban cards
- Local content calculator (input your products → calculate %)
- Link to Ministry of Industry local content verification
- Historical tracking of local content requirement changes

---

## Support

**Email:** contact@icloud-solutions.net  
**Website:** https://icloud-solutions.net

For local content calculation and SME certification questions, refer to:
- Ministry of Industry and Mineral Resources
- Saudi Authority for SMEs (Monsha'at)
- Local Content & Government Procurement Authority (LCGPA)
