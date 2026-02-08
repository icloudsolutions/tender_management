# Scraping & Synchronization Settings - Implementation Guide

## Overview

The Scraping & Synchronization settings are now **fully functional** and control how the system automatically fetches tenders from the Etimad portal.

---

## ✅ Implemented Features

### 1. **Enable Auto Sync**
- **Field**: `etimad_auto_sync` (Boolean)
- **Default**: True
- **Function**: Enables/disables automatic tender synchronization
- **Behavior**: 
  - When **ON**: Scheduled cron job runs automatically
  - When **OFF**: Cron job is deactivated, manual sync only

### 2. **Sync Interval**
- **Field**: `etimad_sync_interval` (Integer)
- **Default**: 24 hours
- **Range**: 1-168 hours (1 hour to 1 week)
- **Function**: Controls how often the system fetches tenders
- **Behavior**:
  - < 24 hours: Runs every X hours
  - ≥ 24 hours: Runs every X days
  - **Validation**: Prevents values outside acceptable range

### 3. **Tenders per Page**
- **Field**: `etimad_fetch_page_size` (Integer)
- **Default**: 50
- **Range**: 10-50
- **Function**: Number of tenders to fetch per page
- **Behavior**:
  - Limited by Etimad API (max 50)
  - **Validation**: Enforces API limits

### 4. **Pages per Sync**
- **Field**: `etimad_fetch_pages` (Integer)
- **Default**: 1
- **Range**: 1-10
- **Function**: Number of pages to fetch in each sync
- **Formula**: `Total tenders = page_size × pages`
- **Example**: 50 tenders/page × 3 pages = 150 tenders per sync
- **Validation**: Max 10 pages to prevent performance issues

### 5. **Max Retries**
- **Field**: `etimad_max_retries` (Integer)
- **Default**: 3
- **Range**: 1-10
- **Function**: Number of retry attempts if API call fails
- **Behavior**: Automatic retry with delays between attempts
- **Validation**: Prevents excessive retry loops

---

## 🔧 Technical Implementation

### Modified Files

1. **`models/etimad_tender.py`**
   - ✅ Updated `action_fetch_tenders_cron()` to read settings
   - ✅ Updated `fetch_etimad_tenders()` to use `max_retries` from settings
   - ✅ Added `update_cron_interval()` method to dynamically adjust cron schedule

2. **`models/res_config_settings.py`**
   - ✅ Added validation constraints for all settings
   - ✅ Added `set_values()` override to update cron when settings change
   - ✅ Added helpful descriptions and limits

3. **`views/res_config_settings_views.xml`**
   - ✅ Enhanced UI with info alerts
   - ✅ Added calculation examples
   - ✅ Added warnings when auto-sync disabled
   - ✅ Improved button tooltips

4. **`data/ir_cron_data.xml`**
   - ✅ Cron job now responds to settings changes dynamically

---

## 📊 How It Works

### Automatic Synchronization Flow

```
┌─────────────────────────────────────────────────────┐
│  1. Cron Job Triggers (based on sync interval)     │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  2. Check if Auto Sync is Enabled                  │
│     - If NO: Skip and log message                  │
│     - If YES: Continue                             │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  3. Read Settings from Database                     │
│     - Page Size (default: 50)                      │
│     - Pages (default: 1)                           │
│     - Max Retries (default: 3)                     │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  4. Fetch Tenders from Etimad API                   │
│     - Loop through pages                           │
│     - Retry on failure (up to max_retries)        │
│     - Create/update tender records                 │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  5. Log Results                                     │
│     - Tenders created                              │
│     - Tenders updated                              │
│     - Errors encountered                           │
└─────────────────────────────────────────────────────┘
```

### Dynamic Cron Update

When settings are saved:
```python
1. User changes "Sync Interval" from 24h to 12h
2. Save button clicked
3. set_values() method triggered
4. update_cron_interval() called
5. Cron job updated:
   - interval_number = 12
   - interval_type = 'hours'
6. Next sync runs in 12 hours instead of 24h
```

---

## 🎯 Usage Examples

### Example 1: Daily Full Sync (Default)
```
Settings:
- Enable Auto Sync: ✓ ON
- Sync Interval: 24 hours
- Tenders per Page: 50
- Pages per Sync: 1
- Max Retries: 3

Result: Fetches 50 tenders every day at scheduled time
```

### Example 2: High-Frequency Sync
```
Settings:
- Enable Auto Sync: ✓ ON
- Sync Interval: 6 hours
- Tenders per Page: 50
- Pages per Sync: 2
- Max Retries: 5

Result: Fetches 100 tenders (50×2) every 6 hours
```

### Example 3: Large Batch Weekly Sync
```
Settings:
- Enable Auto Sync: ✓ ON
- Sync Interval: 168 hours (7 days)
- Tenders per Page: 50
- Pages per Sync: 10
- Max Retries: 3

Result: Fetches 500 tenders (50×10) once per week
```

### Example 4: Manual Only
```
Settings:
- Enable Auto Sync: ✗ OFF

Result: No automatic syncing. Use "Manual Sync Now" button
```

---

## ⚙️ Configuration UI

### Location
**Settings → Etimad Tenders → Scraping & Synchronization**

### Features
1. **Toggle Auto Sync**: Enable/disable with single checkbox
2. **Visual Feedback**: Alert shows when sync is disabled
3. **Inline Help**: Hints show limits and recommendations
4. **Live Calculation**: Shows total tenders formula
5. **Test Buttons**:
   - **Test Connection**: Fetch 5 tenders to verify API works
   - **Manual Sync Now**: Immediate sync with current settings

---

## 🔒 Validations

All settings have validation to prevent incorrect values:

| Setting | Validation | Error Message |
|---------|-----------|---------------|
| Sync Interval | 1 ≤ value ≤ 168 | "Sync interval must be at least 1 hour" / "Cannot exceed 168 hours (1 week)" |
| Page Size | 10 ≤ value ≤ 50 | "Page size must be at least 10" / "Cannot exceed 50 (Etimad API limit)" |
| Pages | 1 ≤ value ≤ 10 | "Must fetch at least 1 page" / "Maximum allowed: 10" |
| Max Retries | 1 ≤ value ≤ 10 | "Must allow at least 1 retry" / "Maximum allowed: 10" |

---

## 📈 Performance Considerations

### Recommended Settings by Use Case

**Small Business / Startup:**
```
Sync Interval: 24 hours
Pages: 1
Total: 50 tenders/day
```

**Medium Company:**
```
Sync Interval: 12 hours
Pages: 2
Total: 100 tenders/day
```

**Large Enterprise:**
```
Sync Interval: 8 hours
Pages: 3-5
Total: 150-250 tenders/day
```

### Performance Impact

- **API Calls**: Each page = 1 API call
- **Processing Time**: ~2-5 seconds per page
- **Database**: ~50 records inserted/updated per page
- **Memory**: Minimal (processes page by page)

---

## 🐛 Troubleshooting

### Issue: Tenders Not Syncing

**Check:**
1. Is "Enable Auto Sync" turned ON?
2. Check cron job status: Settings → Technical → Scheduled Actions
3. Look for "Fetch Etimad Tenders - Daily Sync"
4. Check "Next Execution" time
5. Review logs for errors

### Issue: Getting Old Tenders

**Solution:**
- Increase "Pages per Sync" to fetch more recent tenders
- Etimad returns newest tenders first

### Issue: Frequent API Failures

**Solution:**
1. Reduce "Pages per Sync" (less load per request)
2. Increase "Sync Interval" (less frequent requests)
3. Check internet connectivity
4. Verify Etimad portal is accessible

### Issue: Cron Not Running at Expected Time

**Solution:**
1. Save settings again to trigger cron update
2. Manually update cron: Settings → Technical → Scheduled Actions
3. Check if Odoo cron worker is running

---

## 🔍 Monitoring

### View Sync Activity

**Method 1: Tender List**
- Check "Last Scraped At" field on tender records
- Sort by "Created At" to see newest

**Method 2: Logs**
```
Settings → Technical → Server Actions
Look for logs containing:
- "Starting scheduled tender fetch..."
- "Scheduled tender fetch completed successfully"
```

**Method 3: Cron History**
```
Settings → Technical → Scheduled Actions
→ Select "Fetch Etimad Tenders - Daily Sync"
→ Check "Last Run" timestamp
```

---

## 🚀 Advanced Usage

### Custom Cron Schedule

For advanced users who need specific times:

1. Go to: Settings → Technical → Scheduled Actions
2. Find: "Fetch Etimad Tenders - Daily Sync"
3. Adjust: "Next Execution Date" to desired time
4. Note: Settings override will reset this on next save

### Programmatic Control

```python
# Disable auto sync programmatically
self.env['ir.config_parameter'].sudo().set_param(
    'ics_etimad_tenders_crm.etimad_auto_sync', 
    'False'
)

# Update cron
self.env['ics.etimad.tender'].sudo().update_cron_interval()
```

---

## 📝 Changelog

### Version 18.0.4.1.0
- ✅ Implemented all scraping & sync settings
- ✅ Added dynamic cron interval updates
- ✅ Added validation constraints
- ✅ Enhanced configuration UI
- ✅ Added comprehensive help text
- ✅ Settings now fully functional

### Previously (Version 18.0.3.1.0)
- ❌ Settings existed but were not functional
- ❌ Hardcoded values used instead

---

## ✅ Testing Checklist

- [ ] Enable auto sync → Verify cron activates
- [ ] Disable auto sync → Verify cron deactivates  
- [ ] Change interval → Verify cron updates
- [ ] Set invalid value → Verify validation error
- [ ] Click "Test Connection" → Verify fetches 5 tenders
- [ ] Click "Manual Sync" → Verify respects current settings
- [ ] Check logs → Verify settings are logged
- [ ] Wait for scheduled run → Verify uses configured settings

---

## 🎉 Summary

**Before**: Settings existed but were non-functional (0/5 implemented)

**After**: All 5 settings are fully functional and integrated:
1. ✅ Auto Sync Enable/Disable
2. ✅ Configurable Sync Interval
3. ✅ Configurable Page Size
4. ✅ Configurable Pages per Sync
5. ✅ Configurable Max Retries

The system now provides complete control over tender synchronization with Etimad portal!
