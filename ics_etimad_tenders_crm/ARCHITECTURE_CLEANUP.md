# Architecture Cleanup: Etimad Tender State Management

## Problem Addressed

The `ics_etimad_tenders_crm` module had a **conceptual conflict** in its state management:

### Before (Problematic)

```python
# ics.etimad.tender model had TWO status concepts:

1. state field (Manual tracking)
   - Values: new, in_progress, qualification, won, lost, cancelled
   - Set by USER via buttons ("Mark as Won", "Mark as Lost", etc.)
   - Represented YOUR internal tracking

2. tender_status_id (From Etimad portal)
   - Values: IDs from Etimad API
   - Reflects ACTUAL tender status on government portal
   - Auto-updated during sync
```

**This created confusion:**
- "Won" by us or "Won" on Etimad?
- "Cancelled" by agency or cancelled by us?
- External data mixed with internal tracking

## Solution Implemented

### Architectural Principle

**Etimad tenders = External read-only data source (like weather data)**
- Should reflect the portal status only
- No manual state management
- Users create Opportunities or ICS Tenders for internal tracking

### Changes Made

#### 1. Removed from `ics.etimad.tender` Model

**Deleted:**
- `state` field (Selection with 6 values)
- `action_set_state()` method
- All status buttons from form header
- State-based filters and grouping

**Kept:**
- `tender_status_id` (from Etimad portal)
- `tender_status_text` (from Etimad portal)
- `tender_status_approved` (computed from portal data)

#### 2. Added Simple Tracking

**New field:**
```python
is_participating = fields.Boolean("Participating", default=False,
    help="Mark this if your company is preparing a quotation for this tender")
```

**New action:**
```python
def action_toggle_participating(self):
    """Toggle participation status"""
    self.ensure_one()
    self.is_participating = not self.is_participating
    # Posts message to chatter
```

**New buttons in header:**
- "✅ Mark as Participating" (when not participating)
- "⬜ Unmark Participating" (when participating)

#### 3. Updated Views

**List View:**
- Removed: `state` column
- Added: `tender_status_text` (from Etimad)
- Added: `is_participating` boolean column
- Changed decoration: Bold font for favorites OR participating tenders

**Search Filters:**
- Removed: "New", "In Progress", "Qualification", "Won", "Lost", "Cancelled"
- Added: "👥 Participating", "✅ Approved (Etimad)", "🏆 With Award Results"

**Group By:**
- Removed: "Status" (based on state)
- Added: "Participating" (groups by is_participating)

**Menu Context:**
- Removed default filter: `search_default_state_new`
- Urgent tenders no longer filter by state

## New Architecture

```
┌─────────────────────────────────────┐
│ ics.etimad.tender (External Data)  │
│ - tender_status_id (from portal)   │  ← Read-only from Etimad
│ - tender_status_text (from portal) │
│ - is_participating (simple flag)   │  ← Optional user tracking
│                                     │
│ Actions:                            │
│ • Create Opportunity →              │
│ • Create ICS Tender →               │
│ • Toggle Participating              │
└──────────────┬──────────────────────┘
               │ Creates
               ↓
┌─────────────────────────────────────┐
│ crm.lead (CRM Opportunity)          │
│ OR                                  │
│ ics.tender (Tender Management)      │
│                                     │
│ - state: draft → won/lost          │  ← Full workflow here
│ - Complete participation tracking   │
└─────────────────────────────────────┘
```

## Workflow

### Before
1. Browse Etimad tenders
2. Manually mark as "In Progress", "Won", "Lost" (WRONG!)
3. Confusion between portal status and your status

### After
1. Browse Etimad tenders (shows portal status)
2. Optional: Toggle "Participating" flag for tracking
3. Click "Create Opportunity" OR "Create ICS Tender"
4. Track your participation in proper module with full workflow

## Benefits

### 1. Clear Separation of Concerns
- **Etimad module** = External data scraping & viewing
- **CRM/Tender modules** = Internal participation tracking

### 2. No Data Confusion
- "Won" always means "Won on Etimad portal" (if we add that status)
- Your participation status tracked in proper place (CRM or ICS Tender)

### 3. Better UX
- No ambiguity about what status means
- Clear action flow: Browse external → Create internal → Track

### 4. Maintainability
- Etimad scraper focused on its job: scraping
- No mixing of concerns
- Easier to understand and debug

## Migration Notes

### For Existing Data

If you have existing Etimad tenders with `state` values:

1. **No data loss** - The field is just removed from model, data stays in database
2. **No action needed** - The field wasn't being used meaningfully anyway
3. **Clean slate** - Use `is_participating` going forward

### For Existing Workflows

If users were using state buttons:

1. **Instead of "Mark as Won/Lost"** → Create ICS Tender and track there
2. **Instead of "Mark as In Progress"** → Toggle "Participating" flag
3. **Better tracking** → Use proper CRM Opportunity or ICS Tender workflow

## Integration with ics_tender_management

The `ics_tender_management` module **is not affected** by this change:

```python
# ics_tender_management/models/etimad_tender.py
# Line 86: Still sets state to 'draft' when creating ICS Tender
vals = {
    'tender_title': self.name,
    # ... other fields ...
    'state': 'draft',  # ✅ This is the ICS Tender state, not Etimad state
}
```

The integration works perfectly:
1. Browse `ics.etimad.tender` (no state, just portal data)
2. Click "Create Tender Direct"
3. Creates `ics.tender` with `state='draft'`
4. Full workflow in `ics.tender` (draft → technical → won/lost)

## Testing Checklist

After deploying:

- [ ] Etimad tenders display without errors
- [ ] "Participating" toggle works
- [ ] Chatter message posted when toggling
- [ ] Search filters work (Participating, Approved, Award Results)
- [ ] List view shows `tender_status_text` from portal
- [ ] "Create Opportunity" still works
- [ ] "Create ICS Tender" still works and sets `state='draft'`
- [ ] No references to old `state` field cause errors

## Files Changed

**Commit:** `ae30087` - "Remove internal state management from ics_etimad_tenders_crm - keep only Etimad portal status"

1. **`ics_etimad_tenders_crm/models/etimad_tender.py`**
   - Removed `state` field
   - Added `is_participating` field
   - Replaced `action_set_state()` with `action_toggle_participating()`
   - Removed state mapping from fetch logic

2. **`ics_etimad_tenders_crm/views/etimad_tender_views.xml`**
   - Removed state buttons from header (5 buttons)
   - Added participating toggle buttons (2 buttons)
   - Removed `state` column from list
   - Added `tender_status_text` and `is_participating` columns
   - Updated list decorations
   - Updated search filters
   - Updated group by options
   - Removed state-based default contexts

3. **`ics_etimad_tenders_crm/views/etimad_menus.xml`**
   - Removed `search_default_state_new` from context
   - Updated urgent tenders domain (removed state filter)

## Support

For questions or issues:
- **Email:** contact@icloud-solutions.net
- **Website:** https://icloud-solutions.net
