# Legacy CRM (Odoo Studio) → `ics_tender_management` Migration Assessment

This note is based on the screenshots in `documentation/crm*.png` (legacy CRM Opportunity form customized via Odoo Studio) and the current `ics_tender_management` data model (mainly `ics.tender`).

## 1) What `ics_tender_management` requires (minimum to create an `ics.tender`)

In `ics.tender` the following fields are **required** (or practically required) and must be populated during migration:

- **`partner_id` (Customer)**: legacy `crm.lead.partner_id`
- **`tender_number`**: legacy “Tender Reference Number” / “Tender Number” (must exist; otherwise generate a value)
- **`tender_title`**: legacy `crm.lead.name` (opportunity title)
- **`tender_category`**: legacy “نوع المنافسة / Tender Category” mapping to one of:
  - `supply`, `services`, `construction`, `maintenance`, `consulting`, `other`
- **`tender_type`**: legacy choice between “Single vendor” vs “Product-wise”
- **`submission_deadline`**: legacy “تاريخ التقديم” / submission deadline (required)

Strongly recommended to populate as well:

- **`user_id` (Responsible)**: legacy salesperson
- **`team_id` (Sales Team)**: legacy sales team
- **`expected_revenue`**: legacy expected revenue
- **`announcement_date` / `document_purchase_date` / `opening_date`**: if present
- **`lead_id`**: link the created tender back to the original opportunity for traceability

## 2) What exists in legacy CRM screenshots but is NOT in `ics.tender` today

The screenshots show several “process / compliance” fields that are not implemented in `ics.tender` and would be lost unless we model them.

### A) Procurement / booklet purchase
- Booklet purchased? (boolean)
- Booklet purchase request date / purchase date
- Purchase receipt attachment
- Tender booklet price

### B) Site visit + inquiries
- Documents required for site visit (attachments)
- Last date for inquiries
- Required inquiries/questions (text)

### C) Qualification / approvals workflow
- Approval from Direct Manager / Department Manager / Financial Manager / CEO (booleans)
- “Document upload for review” action + review flags
- Selected suppliers / potential suppliers (partner list)

### D) Opportunity evaluation
- Presales employee
- Evaluation criteria (attachments)
- Required certifications (attachments)
- Project scope of work (text)
- Challenges (text)
- Winning probability, client relationship
- Participation decision + reasons for non-participation

### E) Tender results
- Offers opened + opening date(s)
- Upload competing companies prices (attachments)
- Financial offer accepted + rejection reasons
- Discount requested, appeal submitted
- Offer extension + extension awarded + rejection reason
- Awarded company + amount awarded + award date + award letter attachment

### F) Financial breakdown (legacy totals)
Legacy screenshots show many totals (pre/post tax, financing %, etc.). `ics.tender` currently keeps:
- `total_estimated_cost`
- `total_vendor_cost`
- `margin_percentage`
- `margin_amount`
- `total_quotation_amount`

If you need the extra breakdown (tax, financing, etc.), we should add explicit fields or compute them from existing accounting objects.

## 3) Recommended migration strategy (safe + incremental)

### Option 1 (recommended): migrate in 2 phases
**Phase 1 – Minimal migration (go-live fast):**
- Create `ics.tender` for each legacy opportunity that represents a tender.
- Map only the required fields + the key dates + responsibility fields.
- Push all “extra” legacy data into:
  - `ics.tender.notes` (HTML) / `winning_reason` / `lost_reason`
  - `ir.attachment` linked to the tender (for files)

**Phase 2 – Full fidelity:**
- Create a small extension module (e.g. `ics_tender_management_legacy_bridge`) that adds the missing compliance/approval fields to `ics.tender` (or new related models).
- Write a migration script to copy Studio fields from `crm.lead` to the new tender fields.

### Option 2: keep legacy CRM fields on `crm.lead` and only link
Because `ics_tender_management` already links tenders to CRM (`ics.tender.lead_id`), you can:
- Keep the legacy Studio fields on the opportunity
- Use tenders only for BoQ/vendor selection/PO/quotation/project creation
- This avoids re-implementing every Studio field immediately

## 4) Stage vs Status mapping (legacy → new)

Legacy CRM uses pipeline stages like:
- Under Studying / Qualified / Purchasing tender documents / In Progress / Submission of bids / Tender results …

New module has **two axes**:
- **`stage_id`** (pipeline stage, kanban grouping)
- **`state`** (workflow/statusbar: draft → technical → financial → quotation → submitted → evaluation → won/lost)

During migration, decide:
- Map CRM pipeline stage → `stage_id` (recommended), and optionally also map to `state` where applicable.

## 5) What I recommend you confirm before we implement migration code

1. **Authoritative source for `tender_number`** in legacy (which Studio field is it?)
2. Which legacy “approval” fields must be preserved (and whether they should become real Odoo approvals or just checkboxes).
3. Whether you want **`stage_id`** to be purely visual or enforced to follow **`state`** transitions.

