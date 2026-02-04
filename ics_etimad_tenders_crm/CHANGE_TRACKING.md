# Etimad Tender Change Tracking & Deadline Extension Monitoring

## Overview

The **ics_etimad_tenders_crm** module now includes comprehensive change tracking to monitor updates from the Etimad portal, especially deadline extensions which are critical for users to know about.

## Why This Matters

Etimad tenders reflect **external government portal data**, not internal CRM data. The portal can update tender information at any time:

- **Deadline Extensions** - Government agencies sometimes extend deadlines when companies request more time
- **Financial Changes** - Estimated amounts or fees may be adjusted
- **Date Changes** - Enquiry deadlines, opening dates, etc.

Users need to be **immediately notified** when these changes happen so they can:
- Take advantage of deadline extensions
- Update their quotations if amounts change
- Adjust their preparation timelines

## Features

### 1. Automatic Change Detection

Every time the system fetches tenders from Etimad (daily cron job or manual fetch), it compares new data with existing records and detects:

- **Offers Deadline Changes** (extensions or reductions)
- **Enquiry Deadline Changes**
- **Estimated Amount Changes** (significant changes > 1000 SAR)

### 2. Change History

Each tender tracks:

| Field | Description |
|-------|-------------|
| `previous_offers_deadline` | The deadline before last update |
| `previous_last_enquiry_date` | Enquiry deadline before last update |
| `previous_estimated_amount` | Amount before last update |
| `deadline_extended` | Boolean flag if deadline was extended |
| `deadline_extensions_count` | How many times deadline was extended |
| `last_deadline_extension_date` | When the last extension was detected |
| `has_etimad_updates` | Flag indicating tender has been updated from Etimad |
| `last_significant_change` | Human-readable summary of last change |

### 3. Automatic Notifications

When important changes are detected:

**In Chatter:**
- A message is posted with a summary of changes
- Format: " Etimad Tender Updated" with bullet points for each change
- Example:
  ```
 Etimad Tender Updated
  
  ⏰ Offers deadline EXTENDED by 7 days (new: 2026-02-15 14:00)
  💰 Estimated amount changed: 500,000 → 750,000 SAR (+50.0%)
  ```

**Activity Alert for Deadline Extensions:**
- An activity (To-Do) is automatically created for the responsible user
- Title: "Deadline Extended: [Tender Name]"
- Details include: old deadline, new deadline, days extended
- Links directly to the tender
- If tender is linked to an opportunity, the activity is assigned to the opportunity owner

### 4. Visual Indicators

**In List View:**
- New column: " Extended" (boolean) - shows checkmark for extended deadlines
- Easy to filter and sort by extended tenders

**In Form View:**
- **Button Box:**
  - "Extensions" stat button (green background) shows extension count
  - "Days Left" button has green background if deadline was extended
  
- **Etimad Updates Section:**
  - Shows when `has_etimad_updates` is true
  - Displays deadline extension info
  - Shows previous deadline for comparison
  - Alert box: "Deadline Extended! Check activities for details"
  - Shows full change summary

- **Status Ribbons:**
  - Existing ribbons for Hot Tender, Urgent, Favorite

## How It Works

### Daily Sync Process

1. **Cron Job** runs at 6 AM daily (configurable)
2. **Fetches** latest tender data from Etimad API
3. **For each tender:**
   - Checks if tender already exists (by reference_number or tender_id)
   - **If exists:**
     - Compares critical fields (deadlines, amounts)
     - Detects changes
     - Updates `previous_*` fields before overwriting
     - Sets flags (`deadline_extended`, etc.)
     - Posts to chatter
     - Creates activity for deadline extensions
   - **If new:**
     - Creates tender record as usual

### Manual Operations

Users can also:
- **Fetch Details** button - pulls detailed info from Etimad (dates, award results, etc.)
- **Fetch Batch** - fetches multiple pages of tenders manually
- All manual fetches also include change detection

## Usage Scenarios

### Scenario 1: Deadline Extension Request

**Situation:** Your company needs more time to prepare a quotation and requests an extension from the agency. The agency approves and updates Etimad.

**What Happens:**
1. Next sync (or manual fetch) detects the new deadline
2. Chatter message posted: "⏰ Offers deadline EXTENDED by 5 days"
3. Activity created for you: "Deadline Extended: [Tender Name]"
4. You receive a notification
5. You can now update your preparation timeline

### Scenario 2: Amount Adjustment

**Situation:** Agency realizes the estimated tender value was incorrect and updates it on Etimad.

**What Happens:**
1. System detects: "💰 Estimated amount changed: 1,000,000 → 1,500,000 SAR (+50.0%)"
2. Posted to chatter for audit trail
3. You can review and adjust your quotation accordingly

### Scenario 3: Tracking Updates for Linked Tenders

**Situation:** You created an opportunity or ICS Tender from an Etimad tender and are working on it.

**What Happens:**
- Changes detected in Etimad tender appear in chatter
- If opportunity exists, activity is assigned to opportunity owner
- You stay informed of portal changes even while working on your internal tender/opportunity

## Configuration

### Cron Job Settings

The scheduled action can be configured:
- **Name:** "Fetch Etimad Tenders - Daily Sync"
- **Model:** `ics.etimad.tender`
- **Frequency:** Daily at 6 AM (default)
- **Active:** True

To adjust:
1. Go to **Settings → Technical → Automation → Scheduled Actions**
2. Find "Fetch Etimad Tenders - Daily Sync"
3. Adjust interval or next run time

### Notification Preferences

Currently notifications are automatic for:
- Deadline extensions (activity created)
- All significant changes (chatter message)

Future enhancements could include:
- Email notifications
- Configurable notification rules
- Threshold settings for "significant" changes

## Technical Details

### Change Detection Logic

**Deadline Extension Detection:**
```python
if new_offers_deadline > existing.offers_deadline:
    days_extended = (new_offers_deadline - existing.offers_deadline).days
    # Create notification
```

**Significant Amount Change:**
```python
if abs(new_estimated_amount - existing.estimated_amount) > 1000:  # > 1000 SAR
    change_pct = ((new - old) / old) * 100
    # Log change
```

### Activity Creation

Activities use standard Odoo activity mechanism:
- Type: To-Do
- Assigned to: opportunity owner (if exists) or current user
- Includes direct link to tender
- Rich HTML body with change details

## Best Practices

1. **Check Activities Daily** - Deadline extensions are time-sensitive
2. **Review Chatter** - See full history of Etimad updates on each tender
3. **Filter by Extended** - Use the " Extended" column to find tenders with more time
4. **Link to Opportunities** - When you link an Etimad tender to an opportunity, activities go to the right person
5. **Manual Fetch** - Before important deadlines, click "Fetch Details" to ensure latest data

## FAQ

**Q: How often does the system check for updates?**  
A: Daily at 6 AM by default. You can also fetch manually anytime.

**Q: Will I be notified if a deadline is shortened?**  
A: Yes, the system detects reductions too: "[!] Offers deadline REDUCED by X days"

**Q: What if I miss a notification?**  
A: All changes are logged in the tender's chatter and the "Etimad Updates" section on the form view.

**Q: Can I see the old deadline?**  
A: Yes, the `previous_offers_deadline` field shows the deadline before the change.

**Q: Does this work for tenders I haven't looked at yet?**  
A: Yes, all tenders are monitored. Filter by " Extended" to find any extended tenders.

## Future Enhancements

Potential improvements:
- Email digest of daily changes
- SMS alerts for critical deadline extensions
- Historical change log (table view)
- Custom notification rules per user
- Integration with calendar for deadline reminders
- Automatic quotation deadline adjustment in linked ICS Tenders

## Support

For questions or issues:
- **Email:** contact@icloud-solutions.net
- **Website:** https://icloud-solutions.net
