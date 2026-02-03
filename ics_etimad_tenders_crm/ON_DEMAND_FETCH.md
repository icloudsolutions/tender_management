# On-Demand Tender Fetching

## Overview

In addition to the **automatic daily synchronization** at 6 AM, users can manually fetch tenders from the Etimad portal at any time using multiple convenient methods.

## Methods to Fetch Tenders

### 1. **Menu Items** (Easiest)

Navigate to **Etimad Tenders** in the main menu and click:

- **🔄 Fetch Latest Tenders** - Fetches the latest 50 tenders from Etimad (page 1)
- **🔄 Fetch Batch (150)** - Fetches 150 tenders (3 pages of 50 tenders each)

These menu items are visible to all users and appear right below "Dashboard" in the menu structure.

### 2. **List View Buttons**

When viewing the tender list:

1. Go to **Etimad Tenders → All Tenders**
2. At the top of the list, you'll see two buttons:
   - **🔄 Fetch Latest (50)** - Quick fetch of 50 tenders
   - **🔄 Fetch Batch (150)** - Batch fetch of 150 tenders

These buttons are always visible above the tender list.

### 3. **Kanban View Buttons**

When viewing tenders in Kanban view:

1. Go to **Etimad Tenders → All Tenders**
2. Switch to Kanban view (card view)
3. At the top of the kanban, you'll see:
   - **🔄 Fetch Latest** - Fetches 50 tenders
   - **🔄 Fetch Batch** - Fetches 150 tenders

### 4. **Action Menu** (Advanced)

From the tender list or form view:

1. Select one or more tenders (or open a single tender)
2. Click the **Action** menu (⚙️ gear icon)
3. Choose:
   - **Fetch Etimad Tenders** - Fetches 20 tenders from page 1
   - **Fetch Batch (150 Tenders)** - Fetches 150 tenders (3 pages)

This method is useful when you're already working with tenders and want to update the data.

### 5. **Individual Tender Detail Fetch**

For a specific tender:

1. Open the tender in form view
2. Click **📋 Fetch Details** button (in list view) or **Fetch Detailed Info** (in form view)
3. This fetches additional detailed information from Etimad for that specific tender:
   - Contract duration
   - Insurance requirements
   - Execution locations
   - Award results
   - Additional dates

## Fetch Options Comparison

| Method | Tenders Fetched | Best For |
|--------|----------------|----------|
| **Fetch Latest (50)** | 50 most recent | Quick daily check |
| **Fetch Batch (150)** | 150 most recent | Weekly comprehensive update |
| **Fetch Details** | Single tender (detailed) | Getting complete info for a specific tender |
| **Auto Cron (Daily)** | 50 tenders | Background automation |

## What Happens During Fetch?

1. **Connection** - System connects to Etimad portal API
2. **Retrieval** - Downloads tender data from the portal
3. **Processing** - For each tender:
   - Checks if tender already exists (by reference number or tender ID)
   - **If new:** Creates a new tender record
   - **If exists:** Updates the record and detects changes:
     - Deadline extensions/reductions
     - Amount changes
     - Date updates
4. **Notifications** - For significant changes:
   - Posts message in chatter
   - Creates activity for deadline extensions
   - Updates visual indicators
5. **Result** - Shows notification with summary:
   - Number of tenders created
   - Number of tenders updated
   - Number of pages fetched
   - Any errors encountered

## Success Indicators

After fetching, you'll see a notification like:

```
✅ Tenders Synchronized
15 created, 8 updated from 1 page
```

Or for batch fetch:

```
✅ Tenders Synchronized
45 created, 22 updated from 3 pages
```

## Error Handling

If the fetch fails, you'll see an error message:

- **"Etimad portal is blocking requests"** - The portal has anti-bot protection active. Wait 5-10 minutes and try again.
- **"Failed to fetch any tenders"** - Connection issue or site maintenance. Check internet connection and try later.
- **"X errors"** - Some tenders had issues but others succeeded. Check the log for details.

## Best Practices

### When to Use Each Method

**🔄 Fetch Latest (50):**
- Daily manual check before automatic cron
- After hearing about new tenders
- Quick refresh during business hours

**🔄 Fetch Batch (150):**
- Weekly comprehensive update
- After system downtime
- When catching up after vacation
- Monthly full sync

**📋 Fetch Details:**
- Before creating quotation
- When deadline is near
- To verify award results
- After receiving notification of updates

### Recommended Schedule

1. **Let automatic cron run daily at 6 AM**
2. **Manual fetch at 2 PM** - Mid-day update for new tenders
3. **Batch fetch on Monday mornings** - Start week with full data
4. **Fetch details on-demand** - When working on specific tenders

### Avoiding Rate Limits

Etimad portal has anti-bot protection. To avoid being blocked:

- **Wait 2-3 minutes between manual fetches**
- **Don't fetch batch more than 3-4 times per day**
- **Rely on automatic cron for routine updates**
- If blocked, wait 10-15 minutes before trying again

## Technical Details

### Fetch Latest (50)

```python
# Fetches 50 tenders from page 1
model.fetch_etimad_tenders(page_size=50, page_number=1)
```

### Fetch Batch (150)

```python
# Fetches 3 pages of 50 tenders each
model.fetch_etimad_tenders(page_size=50, page_number=1, max_pages=3)
```

### Retry Mechanism

The fetch system includes automatic retry:
- **3 attempts** per page
- **3-second delay** between attempts
- **2-second delay** between pages

## Monitoring Fetch History

To see fetch history:

1. Go to **Settings → Technical → Automation → Scheduled Actions**
2. Find "Fetch Etimad Tenders - Daily Sync"
3. View the log to see:
   - Last run time
   - Number of executions
   - Any errors

## FAQ

**Q: How often should I manually fetch?**  
A: The automatic daily fetch is usually sufficient. Manual fetch is best for urgent checks or when you need the latest data immediately.

**Q: Will manual fetch interfere with automatic cron?**  
A: No, they work independently. Manual fetches don't affect the scheduled automatic sync.

**Q: What if I fetch and see "0 created, 0 updated"?**  
A: This means all tenders from Etimad are already in your system and haven't changed. This is normal if you fetch multiple times per day.

**Q: Can I fetch more than 150 tenders at once?**  
A: For performance and rate-limiting reasons, the batch fetch is capped at 150. Run multiple batch fetches if you need more, but wait a few minutes between them.

**Q: Will I be notified of changes detected during manual fetch?**  
A: Yes! Manual fetches use the same change detection as automatic sync. Deadline extensions, amount changes, etc. will trigger notifications.

**Q: Can I schedule additional automatic fetches?**  
A: Yes, administrators can create additional scheduled actions:
   1. Go to **Settings → Technical → Automation → Scheduled Actions**
   2. Duplicate "Fetch Etimad Tenders - Daily Sync"
   3. Set your desired schedule (e.g., twice daily at 6 AM and 2 PM)

## Support

For issues with fetching:
- Check your internet connection
- Verify the Etimad portal is accessible: https://tenders.etimad.sa
- Check system logs for detailed error messages
- Contact support: contact@icloud-solutions.net
