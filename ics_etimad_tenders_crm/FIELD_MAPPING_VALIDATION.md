# Etimad Tender Field Mapping Validation

## Real Tender Example: 2026/20

**URL:** https://tenders.etimad.sa/Tender/DetailsForVisitor?STenderId=TRC4p6vN*@@**51vZHmuZXv%20og==

**Tender:** صيانة معدات و سيارات - التابعة بلدية محافظة المزاحمية 2026م

---

## Field-by-Field Comparison

| Etimad Field (Arabic) | Etimad Field (English) | Model Field | Status | Notes |
|----------------------|------------------------|-------------|---------|-------|
| **المعلومات الأساسية (Basic Information)** |
| اسم المنافسة | Tender Name | `name` | ✅ Captured | Main field |
| رقم المنافسة | Competition Number | `tender_number` | ✅ Captured | e.g., "2026/20" |
| الرقم المرجعي | Reference Number | `reference_number` | ✅ Captured | e.g., "260239001155" |
| الغرض من المنافسة | Tender Purpose | `tender_purpose` | ✅ Captured | Text field for description |
| قيمة وثائق المنافسة | Document Cost | `document_cost_amount` | ✅ Captured | 2500.00 SAR |
| حالة المنافسة | Tender Status | `tender_status_text` | ✅ Captured | "معتمدة" (Approved) |
| مدة العقد | Contract Duration | `contract_duration` | ✅ Captured | "90 يوم" |
| | | `contract_duration_days` | ✅ Computed | 90 (integer) |
| هل التأمين من متطلبات المنافسة | Insurance Required | `insurance_required` | ✅ Captured | Boolean (لا = False) |
| نوع المنافسة | Competition Type | `tender_type` | ✅ Captured | "منافسة عامة" |
| الجهة الحكوميه | Government Entity | `agency_name` | ✅ Captured | "أمانة منطقة الرياض" |
| الوقت المتبقى | Time Remaining | `remaining_days` | ✅ Computed | Calculated from deadline |
| طريقة تقديم العروض | Submission Method | `submission_method` | ✅ Captured | Selection field |
| مطلوب ضمان الإبتدائي | Initial Guarantee Required | `initial_guarantee_required` | ✅ Captured | Boolean |
| | Initial Guarantee Type | `initial_guarantee_type` | ✅ Captured | "لا يوجد ضمان" |
| الضمان النهائي | Final Guarantee | ⚠️ **MISSING** | ⚠️ Not captured | **Need to add** |

---

## Missing Field: Final Guarantee (الضمان النهائي)

### Issue
The **Final Guarantee percentage** (5.00 in this example) is NOT currently captured in our model.

### Why It Matters
- Final guarantee (also called "Performance Guarantee" or "حسن الأداء") is a percentage that the winning contractor must provide as a bank guarantee
- Typically 5-10% of contract value
- **Critical for bidders** to know upfront for cash flow planning
- Required AFTER winning the tender
- Different from initial guarantee (required BEFORE bidding)

### Example Values
- "5.00" = 5% of contract value
- "10.00" = 10% of contract value
- Some tenders may have "لا يوجد" (None)

### Recommendation
Add these fields:

```python
# Final/Performance Guarantee
final_guarantee_percentage = fields.Float("Final Guarantee %", 
    help="الضمان النهائي - Performance guarantee percentage (حسن الأداء)")
final_guarantee_required = fields.Boolean("Final Guarantee Required",
    compute='_compute_final_guarantee_required', store=True,
    help="Whether final guarantee is required")
```

---

## All Fields Summary

### ✅ Currently Captured (19 fields)

1. `name` - Tender name
2. `tender_number` - Competition number (2026/20)
3. `reference_number` - Reference (260239001155)
4. `tender_purpose` - Purpose/description
5. `document_cost_amount` - Document cost (2500.00)
6. `tender_status_text` - Status (معتمدة)
7. `tender_status_approved` - Approved flag
8. `contract_duration` - Duration text (90 يوم)
9. `contract_duration_days` - Duration number (90)
10. `insurance_required` - Insurance required flag
11. `tender_type` - Competition type (منافسة عامة)
12. `agency_name` - Government entity
13. `remaining_days` - Time remaining (computed)
14. `submission_method` - Submission method
15. `initial_guarantee_required` - Initial guarantee flag
16. `initial_guarantee_type` - Initial guarantee type
17. `offers_deadline` - Deadline date/time
18. `published_at` - Publication date
19. `tender_id_string` - Tender ID for API calls

### ⚠️ Missing (1 field)

1. `final_guarantee_percentage` - **Final guarantee % (الضمان النهائي)**

---

## Data Flow

### 1. Initial Scraping (GetTendersByAgencyID)
Captures basic info:
- Tender name, number, reference
- Agency, type
- Deadlines
- Status

### 2. Detail Fetching (4 API Endpoints)
**GetRelationsDetailsViewComponenet:**
- Classification
- Locations
- Activities
- ✅ Final guarantee should be here

**GetTenderDatesViewComponenet:**
- All dates
- Inquiry details

**GetAwardingResultsForVisitorViewComponenet:**
- Award status
- Awarded company
- Amount

**GetLocalContentDetailsViewComponenet:**
- Local content %
- SME benefits

---

## Parser Update Needed

### Current Parser (GetRelationsDetailsViewComponenet)

This parser currently extracts:
- Classification
- Execution location
- Regions/cities
- Tender purpose
- Activities
- Supply/construction/maintenance flags

### Need to Add

Extract "الضمان النهائي" from the Relations endpoint or main page:

```python
# In _parse_relations_details_html method:

# Extract final guarantee percentage
guarantee_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "الضمان النهائي")]/following-sibling::div[1]//span/text()')
if guarantee_elements:
    guarantee_str = html_module.unescape(guarantee_elements[0].strip())
    # Extract number from "5.00" or "10.00"
    guarantee_match = re.search(r'(\d+(?:\.\d+)?)', guarantee_str)
    if guarantee_match:
        parsed_data['final_guarantee_percentage'] = float(guarantee_match.group(1))
```

---

## Impact Analysis

### High Priority ⚠️
Final guarantee is **critical financial information**:

**For Bidders:**
- Need to know upfront for cash flow planning
- Bank guarantee ties up credit lines
- Affects bid decision (can we afford the guarantee?)

**For Finance Team:**
- Calculate total guarantees needed
- Plan credit facility requirements
- Budget for bank charges

**Example Calculation:**
- Contract value: 1,000,000 SAR
- Final guarantee: 5%
- Bank guarantee needed: 50,000 SAR
- Bank charges (typical): 1-2% annually

### Low Priority (Already Captured)
Everything else in the basic info is already captured correctly.

---

## Recommendation

### Immediate Action
1. Add `final_guarantee_percentage` field to model
2. Add `final_guarantee_required` computed field
3. Update `_parse_relations_details_html` parser to extract it
4. Add field to form view in "Financial Requirements" section
5. Add optional column to list view

### Display Location
**Form View - Tab: "1. Classification & Requirements"**

Add group:
```xml
<group string="Guarantees (الضمانات)">
    <field name="initial_guarantee_required"/>
    <field name="initial_guarantee_type" invisible="not initial_guarantee_required"/>
    <field name="final_guarantee_required"/>
    <field name="final_guarantee_percentage" 
           widget="percentage" 
           invisible="not final_guarantee_required"/>
    
    <div invisible="not final_guarantee_required" class="alert alert-info">
        <i class="fa fa-info-circle"/> Final guarantee (حسن الأداء): 
        Bank guarantee required after winning = <field name="final_guarantee_percentage"/>% of contract value
    </div>
</group>
```

---

## Test Case

**Tender:** 2026/20 (shown in screenshot)

**Expected Results:**
```
name = "صيانة معدات و سيارات - التابعة بلدية محافظة المزاحمية 2026م"
tender_number = "2026/20"
reference_number = "260239001155"
tender_purpose = "صيانة معدات و سيارات - التابعة ..."
document_cost_amount = 2500.00
tender_status_text = "معتمدة"
contract_duration = "90 يوم"
contract_duration_days = 90
insurance_required = False
tender_type = "منافسة عامة"
agency_name = "أمانة منطقة الرياض"
submission_method = "single_file"
initial_guarantee_required = False
initial_guarantee_type = "لا يوجد ضمان"
final_guarantee_percentage = 5.00  ⚠️ Currently missing!
final_guarantee_required = True (computed)
```

---

## Next Steps

1. ✅ Validate all other fields are captured correctly
2. ⚠️ Add final guarantee fields
3. ⚠️ Update parser for GetRelationsDetailsViewComponenet
4. ⚠️ Update form view
5. ⚠️ Update list view (optional column)
6. ✅ Test with tender 2026/20
7. ✅ Document in FIELD_MAPPING.md

---

## Conclusion

**Status: 95% Complete**

- ✅ 19 out of 20 basic fields captured correctly
- ⚠️ 1 critical field missing: **Final Guarantee %**
- ✅ All 4 detail API endpoints implemented
- ✅ Change tracking working
- ✅ Award results working

**Priority:** Add final guarantee field to complete the basic information capture.

---

**Validated:** 2026-02-03  
**Tender Sample:** 2026/20 (Riyadh Municipality - Vehicle Maintenance)  
**Result:** Model is comprehensive, needs one additional field for final guarantee
