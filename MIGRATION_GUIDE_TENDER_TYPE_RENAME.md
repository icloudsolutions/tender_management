# Migration Guide: tender_type → etimad_tender_type

**Date:** 2026-02-03  
**Change Type:** Field Rename (Breaking Change)  
**Affects:** `ics_etimad_tenders_crm` module

---

## 📋 Summary

Renamed field `tender_type` to `etimad_tender_type` in the `ics.etimad.tender` model to eliminate semantic confusion with the `tender_type` field in `ics.tender` model.

### Semantic Clarification
- **Before:** `tender_type` (Char) - ambiguous naming
- **After:** `etimad_tender_type` (Char) - clearly indicates this is Etimad's classification
  
**Why this matters:**
- `ics.etimad.tender.etimad_tender_type`: Classification text from Etimad portal (e.g., "منافسة عامة", "Public Tender")
- `ics.tender.tender_type`: Internal vendor selection strategy (Selection: `single_vendor` or `product_wise`)

These represent **completely different concepts** and should not share the same field name.

---

## 🔄 Migration Process

### Automatic Migration
The module includes a pre-migration script that will automatically:
1. Check if the `tender_type` column exists in `ics_etimad_tender` table
2. Rename it to `etimad_tender_type` if found
3. Skip if already migrated or on fresh installation

**Migration Script Location:**  
`ics_etimad_tenders_crm/migrations/18.0.1.1/pre-migration.py`

### Manual Steps Required

#### Step 1: Upgrade the Module
```bash
# Via Odoo CLI
./odoo-bin -u ics_etimad_tenders_crm -d your_database

# Or via web interface:
# Apps → ics_etimad_tenders_crm → Upgrade
```

#### Step 2: Verify Migration Success
```sql
-- Check the column was renamed
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'ics_etimad_tender' 
AND column_name IN ('tender_type', 'etimad_tender_type');

-- Should return only 'etimad_tender_type'
```

#### Step 3: Check Data Integrity
```sql
-- Verify no data was lost
SELECT COUNT(*), COUNT(etimad_tender_type) 
FROM ics_etimad_tender;

-- Sample data to verify values preserved
SELECT name, etimad_tender_type 
FROM ics_etimad_tender 
WHERE etimad_tender_type IS NOT NULL 
LIMIT 10;
```

---

## 📝 Changes Made

### 1. Python Model (`models/etimad_tender.py`)
```python
# BEFORE:
tender_type = fields.Char("Tender Type", tracking=True)

# AFTER:
etimad_tender_type = fields.Char("Etimad Tender Type", tracking=True)
```

**Also updated:**
- Line 234: `@api.depends()` decorator
- Line 277: Matching score computation logic
- Line 512: Data processing method

### 2. XML Views (`views/etimad_tender_views.xml`)
Updated all `<field name="tender_type">` references to `<field name="etimad_tender_type">`:
- List view (tree)
- Form view
- Kanban view
- Search filters (Group By)

### 3. Cross-Module References
**`ics_tender_management/models/etimad_tender.py`:**
- Line 51: Updated `_map_tender_category()` call

**`ics_tender_management/models/crm_lead.py`:**
- Line 192: Updated `_map_tender_category_from_etimad()` method

---

## ⚠️ Breaking Changes & Compatibility

### For Custom Code
If you have **custom code** that references `tender_type` on `ics.etimad.tender` records, update it:

```python
# BEFORE (will break):
etimad_record.tender_type

# AFTER:
etimad_record.etimad_tender_type
```

### For External Integrations
If you have API calls or external scripts accessing this field via XML-RPC or JSON-RPC:

```python
# BEFORE:
tender_data = models.execute_kw(
    db, uid, password,
    'ics.etimad.tender', 'search_read',
    [[]], {'fields': ['name', 'tender_type']}
)

# AFTER:
tender_data = models.execute_kw(
    db, uid, password,
    'ics.etimad.tender', 'search_read',
    [[]], {'fields': ['name', 'etimad_tender_type']}
)
```

### For Saved Filters/Dashboards
Users with saved filters or dashboard widgets that reference `tender_type` will need to recreate them after upgrade.

---

## ✅ Testing Checklist

After migration, verify:

- [ ] Module upgrades without errors
- [ ] Etimad tender list view displays "Etimad Type" column correctly
- [ ] Form view shows "Etimad Type" field with correct data
- [ ] Kanban view groups by Etimad Type correctly
- [ ] Search filters (Group By → Etimad Type) work
- [ ] No linter errors in Python files
- [ ] XML views validate successfully
- [ ] Creating ICS Tender from Etimad still works
- [ ] Creating CRM Opportunity from Etimad still works
- [ ] Data scraping from Etimad portal populates the field correctly

---

## 🔙 Rollback Procedure

If issues occur, you can rollback the database changes:

```sql
-- Rename column back (if needed)
ALTER TABLE ics_etimad_tender 
RENAME COLUMN etimad_tender_type TO tender_type;

-- Then restore the previous module version
```

⚠️ **Important:** Always backup your database before major migrations!

---

## 📞 Support

If you encounter issues:
1. Check Odoo logs for migration errors
2. Verify the database column was renamed successfully
3. Clear browser cache and reload Odoo interface
4. Restart Odoo service if views don't update

---

## 📚 Related Documentation

- `FIELD_DUPLICATION_REPORT.md` - Full analysis of field naming conflicts
- Module `__manifest__.py` - Updated to version 18.0.1.1
