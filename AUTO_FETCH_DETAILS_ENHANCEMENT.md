# Auto-Fetch Details Enhancement

**Date:** 2026-02-03  
**Change Type:** Feature Enhancement  
**Affects:** `ics_etimad_tenders_crm` module

---

## Summary

Changed the data fetching behavior to automatically retrieve ALL tender details during initial import, eliminating the need to manually click "Fetch Details" for every new tender.

### Before
- **List sync** fetched only basic data (name, agency, deadline, fees)
- Users had to **manually click "Fetch Details"** for EVERY tender to get:
  - Classification & requirements
  - Complete dates & deadlines
  - Local content & SME info
  - Award results
  - Execution locations

### After
- **List sync** automatically fetches ALL details for NEW tenders
- **"Fetch Details" button** is now used only for:
  - Refreshing existing tender data
  - Updating tenders with latest Etimad changes
  - Manual re-sync when needed

---

## Changes Made

### 1. Automatic Detail Fetch on Creation

**File:** `models/etimad_tender.py`

**Method:** `_process_tender_data()`

```python
# NEW: After creating a new tender, auto-fetch all details
else:
    # New tender - create and fetch full details immediately
    new_tender = self.create(vals)
    _logger.info(f"Created tender: {vals['name'][:50]}")
    
    # Auto-fetch detailed info for new tenders (if tender_id_string exists)
    if new_tender.tender_id_string:
        try:
            new_tender._fetch_detailed_info_silent()
            _logger.info(f"Auto-fetched details for new tender: {vals['name'][:50]}")
        except Exception as e:
            _logger.warning(f"Could not auto-fetch details for {vals['name'][:50]}: {e}")
    
    return True
```

**Impact:**
- NEW tenders get full data automatically during sync
- No manual "Fetch Details" needed for new tenders
- Slightly longer sync time (but complete data immediately)

---

### 2. Silent Detail Fetch (for batch operations)

**New Method:** `_fetch_detailed_info_silent()`

```python
def _fetch_detailed_info_silent(self):
    """Fetch detailed info without showing notification (for batch operations)"""
    self.ensure_one()
    if not self.tender_id_string:
        return
    
    try:
        session = self._setup_scraper_session()
        update_vals = self._fetch_all_detail_endpoints(session)
        
        # Remove counter before writing
        update_vals.pop('_fetched_count', None)
        
        if update_vals:
            self.write(update_vals)
            _logger.info(f"Fetched {len(update_vals)} detail fields for tender {self.name}")
    except Exception as e:
        _logger.warning(f"Error in silent detail fetch for {self.name}: {e}")
```

**Purpose:**
- Used during batch import (no UI notifications)
- Logs to server logs only
- Errors don't stop the batch process

---

### 3. Manual "Fetch Details" with View Refresh

**Method:** `action_fetch_detailed_info()` - ENHANCED

**Before:**
- Showed notification
- View did NOT refresh automatically

**After:**
- Fetches details from all 4 endpoints
- Posts message to chatter
- **Automatically refreshes the view** to show updated data
- Returns `ir.actions.act_window` to reload form

```python
# Return action to reload the current record
return {
    'type': 'ir.actions.act_window',
    'res_model': 'ics.etimad.tender',
    'res_id': self.id,
    'view_mode': 'form',
    'target': 'current',
    'context': {'form_view_initial_mode': 'readonly'},
}
```

---

### 4. Shared Detail Fetching Logic

**New Method:** `_fetch_all_detail_endpoints(session)`

**Purpose:** Central method to fetch from all 4 detail API endpoints

**Endpoints Fetched:**
1. **GetRelationsDetailsViewComponenet** - Classification, locations, work types, final guarantee, **tender status text**
2. **GetTenderDatesViewComponenet** - Complete timeline, suspension period
3. **GetAwardingResultsForVisitorViewComponenet** - Award results if announced
4. **GetLocalContentDetailsViewComponenet** - Local content & SME requirements

**Returns:** Dictionary with all parsed data + `_fetched_count` (number of successful endpoint calls)

---

### 5. Tender Status Text Now Populated

**Issue Fixed:** `tender_status_text` was often empty

**Solution (3 sources):**

#### A. From List API
```python
'tender_status_text': (
    raw_data.get('tenderStatusName')
    or raw_data.get('tenderStatus')
    or raw_data.get('statusName')
    or raw_data.get('statusText')
    or raw_data.get('status')
),
```

#### B. From Relations HTML (XPath)
```python
# Extract tender status (حالة المنافسة)
status_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "حالة المنافسة")]/following-sibling::div[1]//span/text()')
if status_elements:
    parsed_data['tender_status_text'] = html_module.unescape(status_elements[0].strip())
```

#### C. From Relations HTML (Regex Fallback)
```python
# Extract tender status (حالة المنافسة)
status_match = re.search(r'حالة المنافسة.*?<span>\s*(.*?)\s*</span>', html_content, re.DOTALL)
if status_match:
    status_text = re.sub(r'<[^>]+>', '', status_match.group(1)).strip()
    if status_text:
        parsed_data['tender_status_text'] = html_module.unescape(status_text)
```

---

## User Experience Changes

### Workflow: NEW Tender Import

**OLD Workflow:**
1. Click "Fetch Latest (50)"
2. See basic tender info (name, agency, deadline, value)
3. Click each tender → Click "Fetch Details" → Wait → View refreshes
4. Repeat for every tender you want full info on

**NEW Workflow:**
1. Click "Fetch Latest (50)"
2. System automatically fetches ALL details for new tenders
3. View complete tender data immediately
4. No manual "Fetch Details" needed!

**Time Savings:** ~90% reduction in manual clicks for new tenders

---

### Workflow: UPDATE Existing Tender

**Use "Fetch Details" button when:**
- Deadline was extended on Etimad portal
- Award results were announced
- Classification or requirements changed
- You want to refresh data for an existing tender

**After clicking:**
- Data is fetched
- Record is automatically updated
- **View refreshes** to show new data
- Message posted to chatter with update summary

---

## Performance Considerations

### Sync Time Impact

**Estimated Time per Tender:**
- Basic data only: ~0.5 seconds
- With detail fetch: ~3-5 seconds (4 API calls + parsing)

**For 50 tenders:**
- Basic sync: ~25 seconds
- With auto-details: ~2.5-4 minutes

**Mitigation:**
- Each endpoint has error handling (failures don't stop the process)
- Batch processing with delays to avoid rate limiting
- Detailed logging for troubleshooting

---

## Configuration (Future Enhancement)

**Potential Setting to Add:**

```python
etimad_auto_fetch_details_on_create = fields.Boolean(
    'Auto-Fetch Details for New Tenders',
    default=True,
    help='Automatically fetch detailed information when creating new tenders'
)
```

This would let users toggle between:
- **Fast sync** (basic data only)
- **Complete sync** (with auto-detail fetch)

---

## Technical Notes

### Error Handling

- If detail fetch fails for a new tender, basic data is still saved
- Errors are logged but don't stop the batch process
- User can manually click "Fetch Details" later if auto-fetch failed

### Rate Limiting

- 2-second delay between pages during batch import
- Individual API calls within detail fetch have no added delay
- Etimad's anti-bot protection may still trigger if too many requests

### Logging

```
[INFO] Created tender: صيانة معدات...
[INFO] Auto-fetched details for new tender: صيانة معدات...
[WARNING] Could not auto-fetch details for منافسة...: Connection timeout
```

---

## Testing Checklist

After upgrade:

- [ ] Click "Fetch Latest (50)"
- [ ] Check that NEW tenders have:
  - Classification field filled
  - Execution locations filled
  - Local content data (if applicable)
  - Complete dates
  - Tender status text filled
- [ ] Click "Fetch Details" on existing tender
- [ ] Verify view refreshes automatically
- [ ] Check chatter for "Details Updated" message
- [ ] Verify no performance issues with batch import

---

## Benefits

1. **Better UX** - Complete data immediately, no manual fetch needed
2. **More accurate** - All fields populated from day 1
3. **Better decisions** - See local content & classification without extra clicks
4. **Time savings** - Eliminate repetitive "Fetch Details" clicks
5. **Auto-refresh** - View updates after manual detail fetch

---

## Related Files Modified

- `ics_etimad_tenders_crm/models/etimad_tender.py`:
  - `_process_tender_data()` - Auto-fetch on create
  - `_fetch_detailed_info_silent()` - New silent fetch method
  - `action_fetch_detailed_info()` - Enhanced with view refresh
  - `_fetch_all_detail_endpoints()` - New shared fetch logic
  - `_parse_relations_details_html()` - Added tender status extraction
  - `_parse_relations_details_regex()` - Added tender status fallback

---

## Migration Notes

- No database migration required
- Existing tenders keep their current data
- New tenders after upgrade get auto-detail fetch
- "Fetch Details" button still works for updates

---

## Future Enhancements

1. **Progress bar** during batch sync with detail fetch
2. **Settings toggle** to enable/disable auto-fetch
3. **Selective detail fetch** - Only for tenders matching filters
4. **Background jobs** - Offload detail fetch to queue for very large batches
