# Smart Matching System — User Guide (English)

## Overview

The **Smart Matching** system in ICS Etimad Tenders CRM automatically classifies and routes tenders using **dynamic rules**. When a tender is created or updated, active rules are evaluated in sequence; each rule can assign a user, mark the tender as favorite, or add notes/reasons based on conditions you define.

Smart Matching works alongside the existing **Match Score** (computed from preferred activities, agencies, and categories). Dynamic rules add **custom, configurable actions** without changing code.

---

## When Rules Run

| Trigger | Description |
|--------|-------------|
| **New tender** | When a tender is created (e.g. fetched from Etimad), all active rules are applied. |
| **Tender updated** | When any tender is saved (write), rules run again. |
| **Manual** | Use **Apply Matching Rules** from the tender list (header) or form to re-run rules on selected or current tender(s). |

Rules run only if **Smart Matching** is enabled in **Etimad Tenders → Configuration → Settings → Smart Matching**.

---

## Where to Configure

- **Enable/disable Smart Matching:**  
  **Etimad Tenders** → **Configuration** → **Settings** → **Smart Matching** tab → **Enable Smart Matching**.

- **Create and edit rules:**  
  **Etimad Tenders** → **Configuration** → **Dynamic Matching Rules**  
  Or from Settings → **Manage Dynamic Rules**.

---

## Rule Structure

Each rule has:

1. **Condition** — *When* the rule applies (which tender field, operator, and value).
2. **Action** — *What* to do when the condition matches (assign user, set favorite, add note, add reason).

Rules are evaluated in **sequence order** (lowest number first). Multiple rules can match the same tender; their actions are combined (e.g. one rule assigns a user, another adds a note).

---

## Condition: Fields

You can base conditions on these tender fields:

| Field | Description |
|-------|-------------|
| **Tender Name** | Full title of the tender. |
| **Agency Name** | Issuing agency (e.g. ministry, authority). |
| **Activity Name** | Tender activity / business area. |
| **Tender Type** | Etimad type (supply, services, etc.). |
| **Description** | Tender description text. |
| **Estimated Amount** | Financial value (numeric). |
| **Remaining Days** | Days until deadline (numeric). |
| **Document Cost** | Cost of tender documents (numeric). |
| **Contract Duration (Days)** | Contract length in days (numeric). |
| **Tender Purpose** | Purpose / scope text. |
| **Activity Details** | Detailed activity text. |
| **Execution Regions** | Regions where work is performed. |
| **Execution Cities** | Cities where work is performed. |

---

## Condition: Operators

### Text fields (name, agency, activity, description, etc.)

| Operator | Meaning | Example |
|----------|--------|--------|
| **Contains** | Field contains the given text (case-insensitive). | Agency contains "وزارة" |
| **Does Not Contain** | Field does not contain the text. | Name does not contain "consulting" |
| **Equals** | Exact match (case-insensitive). | Activity equals "IT Services" |
| **Not Equals** | Not equal. | Type not equals "Supply" |
| **Starts With** | Field starts with text. | Name starts with "توريد" |
| **Ends With** | Field ends with text. | Name ends with "صيانة" |
| **Regex Match** | Regular expression. | Name matches `(IT\|تقنية)` |
| **In List** | Field value is one of comma-separated values. | Value (text): `IT, Software, تقنية` |
| **Is Empty** | Field is empty or not set. | No value needed. |
| **Is Not Empty** | Field has any value. | No value needed. |

### Numeric fields (Estimated Amount, Remaining Days, Document Cost, Contract Duration)

| Operator | Meaning | Example |
|----------|--------|--------|
| **Greater Than** | Field > value | Estimated Amount > 1,000,000 |
| **Greater or Equal** | Field ≥ value | Remaining Days ≥ 14 |
| **Less Than** | Field < value | Document Cost < 5000 |
| **Less or Equal** | Field ≤ value | Remaining Days ≤ 7 |
| **Equals** / **Contains** / **In List** | Use **Value (text)** or **Value (number)**. | e.g. Value (number): 500000 |

- For **Greater/Less** operators, use **Value (number)** or **Value (text)** (e.g. `1000000`).
- **Is Empty** / **Is Not Empty** work on numeric fields (empty = zero or not set).

---

## Actions

When a rule’s condition matches, one of these actions is applied:

| Action | Description | What you set |
|--------|-------------|--------------|
| **Assign to User** | Set the tender’s **Assigned To** field. | **Assign to:** select a user. |
| **Mark as Favorite** | Set the tender as **Favorite**. | Nothing else. |
| **Append to Internal Notes** | Add text to the tender’s **Internal Notes**. | **Value:** the note text. |
| **Append to Match Reasons** | Add text to **Dynamic Match Reasons** (shown with computed match reasons). | **Value:** the reason text. |

- **Assigned To** and **Dynamic Match Reasons** appear on the tender form (CRM Integration area and list/kanban if configured).
- If several rules match, their effects are combined (e.g. one assigns a user, another adds a note).

---

## Step-by-Step: Creating a Rule

1. Go to **Etimad Tenders** → **Configuration** → **Dynamic Matching Rules**.
2. Click **New**.
3. **Rule**
   - **Name:** e.g. "High value IT tenders".
   - **Sequence:** lower = applied first (e.g. 10, 20).
   - **Active:** checked.
4. **Condition** tab
   - **Field:** e.g. **Estimated Amount**.
   - **Operator:** e.g. **Greater Than**.
   - **Value (number):** e.g. `1000000`.
   - For text: use **Value (text)** (e.g. "وزارة", "IT").
5. **Action** tab
   - **Action:** e.g. **Assign to User**.
   - **Assign to:** choose the salesperson.
6. Save.

The rule will run on every create/update when Smart Matching is enabled, and when you click **Apply Matching Rules**.

---

## Examples

### Example 1: Assign high-value tenders to a senior salesperson

- **Condition:** Field = **Estimated Amount**, Operator = **Greater Than**, Value (number) = `5000000`.
- **Action:** **Assign to User** → select the user.

### Example 2: Mark urgent tenders as favorite

- **Condition:** Field = **Remaining Days**, Operator = **Less or Equal**, Value (number) = `7`.
- **Action:** **Mark as Favorite**.

### Example 3: Tag tenders from a specific agency

- **Condition:** Field = **Agency Name**, Operator = **Contains**, Value (text) = `الرياض`.
- **Action:** **Append to Match Reasons**, Value = `Preferred agency (Riyadh)`.

### Example 4: Note for IT-related tenders

- **Condition:** Field = **Activity Name**, Operator = **Contains**, Value (text) = `IT`.
- **Action:** **Append to Internal Notes**, Value = `IT team to review.`.

### Example 5: Multiple values (in list)

- **Condition:** Field = **Tender Type**, Operator = **In List**, Value (text) = `Supply, توريد, Services`.
- **Action:** **Mark as Favorite** or **Assign to User**.

---

## Manual Re-run: Apply Matching Rules

- **From list:** Select one or more tenders → click **Apply Matching Rules** in the list header.
- **From form:** Open a tender → click **Apply Matching Rules** in the action bar.

This re-evaluates all active rules for the selected tender(s) and updates **Assigned To**, **Favorite**, **Internal Notes**, and **Dynamic Match Reasons** accordingly.

---

## Tips

- Use **Sequence** to control order (e.g. general rules first, then specific ones).
- Disable a rule with **Active** unchecked instead of deleting it.
- **Regex** is useful for complex patterns (e.g. multiple keywords); test values to avoid errors.
- **In List** values are comma-separated; spaces after commas are allowed.
- Numeric comparisons use **Value (number)** or **Value (text)**; for amounts you can use `1000000` or `1,000,000` (comma may be stripped where supported).

---

## Summary

| Item | Location / Action |
|------|-------------------|
| Enable Smart Matching | Configuration → Settings → Smart Matching |
| Create/edit rules | Configuration → Dynamic Matching Rules |
| When rules run | On tender create, update, or "Apply Matching Rules" |
| Condition | One field + operator + value(s) |
| Actions | Assign user, Mark favorite, Append note, Append match reason |

For technical details (models, fields, methods), see the module code in `ics_etimad_tenders_crm` (e.g. `models/etimad_matching_rule.py`, `models/etimad_tender.py`).
