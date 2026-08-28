# SMB-SOP-1 Implementation in Odoo 18 Enterprise

## 1. Summary of SMB-SOP-1

The **SMB Division SOP** defines the workflow across six departments:

| Department | Main responsibilities |
|------------|------------------------|
| **Sales** | Receive RFQs → Check stock → Create quotation (margin + delivery buffer) → Follow-up/discount approval → Send P.O. to Credit Control → Handle approved/rejected P.O. → Critical orders coordination |
| **Credit Control** | Review P.O. by payment history & credit limit → Approve or reject → Notify sales (rejection: request payment clearance or credit limit increase) |
| **Logistics** | Receive approved P.O. → Check stock → Issue Delivery Note → Full/partial delivery → Send docs for invoicing → Verify invoices → Deliver invoices to customer |
| **Purchasing** | Procure on request from Logistics; stock procurement for fast-moving/consumables; negotiate with suppliers; issue P.O. |
| **Inventory** | Monitor fast/regular items; target slow-moving clearance; avoid overstock |
| **Collection** | Monthly SoA to credit customers; follow-up (phone/visit); escalate to Sales if needed; legal for disputes/bankruptcy |

All departments are **interlinked** (one order flows: Sales → Credit → Logistics → Invoicing → Collection).

---

## 2. Recommendation: New Module vs Extend ics_tender_management

### Recommended: **New module** (e.g. `ics_smb_workflow`)

| Criteria | New module | Extend ics_tender_management |
|---------|------------|------------------------------|
| **Scope** | SMB-SOP-1 is **order-to-cash** (RFQ → Quote → PO → Credit → Delivery → Invoice → Collection). ics_tender_management is **tender lifecycle** (lead → BOQ → vendor comparison → quote → submit → win/lose → project). | Different business processes in one module. |
| **Users** | SMB division (sales, credit, logistics, purchasing, inventory, collection). | Tender team + SMB; menus and security get mixed. |
| **Dependencies** | Can depend on `sale_management`, `stock`, `account`, and **optionally** `ics_tender_management` when sale orders come from won tenders. | Already heavy; adding SMB adds more complexity. |
| **Upgrades** | Upgrade SMB workflow without touching tender logic. | Risk of breaking tender flows when changing SMB. |
| **Clarity** | Clear separation: “Tender” vs “SMB daily operations”. | One large module handling two distinct procedures. |

**When to extend ics_tender_management instead:**  
Only if you want SMB-SOP-1 to exist **only** for orders that originate from won tenders and you are sure you will never use the same SMB flow for non-tender orders. Even then, a small **bridge** module that depends on both is usually cleaner than merging everything into ics_tender_management.

**Conclusion:** Implement SMB-SOP-1 in a **new module** `ics_smb_workflow` (or `ics_smb_sop`). Add an **optional** dependency on `ics_tender_management` so that sale orders created from won tenders can go through the same credit → logistics → collection flow.

---

## 3. Odoo 18 Enterprise Mapping to SMB-SOP-1

| SMB-SOP-1 area | Odoo 18 app / feature | Usage |
|----------------|------------------------|--------|
| **Sales – RFQ / Quotation** | **Sale** (sale_management) | Use **Quotation** (sale.order) as “quotation”; optional **CRM** for RFQ as lead/opportunity. |
| **Sales – Margin / discount** | Sale: pricelist, margin, discount | Pre-approved margin: pricelist + optional **approval rule** (e.g. discount above X% → Sales Manager). |
| **Credit Control** | **Credit limit** on partner (account or sale) | Use **partner credit limit** + **overdue/outstanding** (account.move, account.payment). Custom: “P.O. sent to Credit Control” state and approval button. |
| **Logistics – Delivery** | **Inventory** (stock) | Delivery Order = Delivery Note; partial/full delivery; backorder. |
| **Logistics – Invoicing** | **Invoicing** (account) | Invoice from delivery (invoice policy: delivered quantities); link Delivery Note ↔ Invoice. |
| **Purchasing** | **Purchase** (purchase) | RFQ to suppliers; P.O.; optional **purchase_requisition** for internal request from Logistics. |
| **Inventory – Monitoring** | **Inventory** (stock) | Reordering rules; reports (slow/fast moving); scrap and clearance. |
| **Collection** | **Invoicing** (account) + **CRM** | Aged receivable; follow-up activities; optional **Statements** (SoA) and automated email (cron). |

---

## 4. New Module: `ics_smb_workflow` – Implementation Plan

### 4.1 Module skeleton

- **Technical name:** `ics_smb_workflow`
- **Category:** Sales or Invoicing
- **Depends (minimal):**  
  `base`, `sale_management`, `stock`, `account`  
  Optional: `ics_tender_management` (if sale orders from tenders use the same flow)
- **Odoo version:** 18.0

### 4.2 Data model (extensions)

1. **Sale Order** (`sale.order` inherit)  
   - `smb_credit_state`: selection  
     `draft` → `sent_to_credit` → `credit_approved` / `credit_rejected`  
   - `smb_credit_approved_by`, `smb_credit_approved_date`  
   - `smb_credit_reject_reason` (for rejection)  
   - `smb_critical_order`: boolean (critical orders → coordination with logistics)  
   - Optional: `tender_id` (if depends on ics_tender_management) already exists there; no duplicate needed.

2. **Partner** (`res.partner` inherit)  
   - Use standard **credit_limit** and **credit** (current exposure) if available in Odoo 18; else add fields for “approved credit limit” and computed “total exposure” (receivables + draft invoices + current SOs).

3. **Optional: SMB Config** (`res.company` or `ir.config_parameter`)  
   - “Require credit approval before confirming SO” (or before delivery).  
   - “Sales Manager approval for discount above X%”.

### 4.3 Workflow (Sales + Credit Control)

- **Sales:**  
  - Create quotation (sale.order) with margin/delivery buffer (pricelist + dates).  
  - On “Send by email” or “Request approval” → set `smb_credit_state = sent_to_credit` and notify Credit Control (mail thread or activity).

- **Credit Control:**  
  - Button “Approve” / “Reject” on sale order.  
  - Approve: check `partner.credit_limit` vs exposure (receivables + orders); if OK → `smb_credit_state = credit_approved`, then allow **Confirm** (and optionally auto-confirm).  
  - Reject: set `smb_credit_state = credit_rejected`, fill `smb_credit_reject_reason`, notify sales; SO stays in quotation or draft.

- **P.O. rejection (SOP):**  
  - Implement as “Credit Rejected”: sales person informs customer and requests payment clearance; after payment, sales can resubmit for credit (e.g. reset to `sent_to_credit` or new SO).

### 4.4 Workflow (Logistics)

- Use standard **Delivery Orders** (stock.picking):  
  - When SO is confirmed, delivery order(s) created by Odoo.  
  - Optional: add a **stage or state** on picking (e.g. “Ready for delivery” → “Delivered”) and “Delivery Note” report (standard or custom).  
  - Partial delivery: standard partial validation; backorder for remaining.  
  - “Delivery Notes and P.O. copies sent for invoicing”: ensure **invoice policy = “Delivered quantities”** and train users to create invoice from SO after delivery.

- Optional:  
  - Custom “Send to Invoicing” button that creates the invoice (or opens wizard) and sets an internal state so logistics can “Verify invoice and deliver to customer” (checklist or stage).

### 4.5 Workflow (Purchasing)

- **Request from Logistics:**  
  - Use **Purchase Requisition** (purchase_requisition) or a simple “Internal Request” (mail/activity to Purchasing) when stock is missing; Purchasing creates RFQ/PO to supplier.  
- **Stock procurement:**  
  - Reordering rules (stock.warehouse, product form) for fast-moving/consumables; optional report “Products to reorder” for Purchasing.

### 4.6 Workflow (Inventory)

- **Stock monitoring:**  
  - Use **Inventory reports** (valuation, movement); optional custom report “Slow-moving / fast-moving” (e.g. by last move date, quantity).  
- **Clearance:**  
  - Scrap or special Pricelist for clearance; optional “Clearance” flag on product or category.

### 4.7 Workflow (Collection)

- **Monthly SoA:**  
  - **Invoicing → Customer Statements** (partner ledger / statement); schedule **Automated Action** or **Cron** to send statement by email to all credit customers (template with PDF attachment if available in Odoo 18).  
- **Follow-up:**  
  - **Follow-up levels** (account.followup) and **activities** (call/visit) on partner or on overdue invoices.  
- **Coordination with Sales:**  
  - When follow-up level “Escalate to Sales” is reached, create **activity for Sales person** (assign to partner’s salesperson).  
- **Dispute / Legal:**  
  - Optional: “Dispute” / “Legal” stage on invoice or partner; route to legal (e.g. activity assigned to legal user).

### 4.8 Security and visibility

- **Credit Control:**  
  - Group “Credit Control” with read/write on `sale.order` (credit fields) and possibly on `res.partner` (credit limit).  
  - Only Credit Control (and above) can click “Approve” / “Reject”.  
- **Sales:**  
  - Can set “Sent to Credit” but not approve.  
- **Logistics:**  
  - Access to Delivery Orders and (if used) “Ready for invoicing” state.  
- **Collection:**  
  - Access to Invoicing (receivables, follow-up, statements).

### 4.9 Reports and prints

- **Delivery Note:** Use standard delivery slip or customize to match “Delivery Note” wording.  
- **Statement of Account (SoA):** Standard **Customer Statement**; schedule monthly email.  
- **P.O. for customer:** Standard sale order report (sent to customer); “Approved” stamp can be a watermark when `smb_credit_state == credit_approved` (optional).

---

## 5. Implementation Steps (Checklist)

1. Create module `ics_smb_workflow` with `__manifest__.py` (depends: sale_management, stock, account; optional ics_tender_management).  
2. Extend `sale.order`: add `smb_credit_state`, approval/rejection fields, and `smb_critical_order`.  
3. Add Credit Control approval/rejection logic (with partner credit limit and overdue check).  
4. Add security group “Credit Control” and access rights; restrict Approve/Reject to that group.  
5. Configure SO invoice policy to “Delivered quantities”; document Logistics flow (delivery → invoice → send invoice to customer).  
6. Optional: extend `stock.picking` with “Delivery Note” print and internal state for “Sent for invoicing”.  
7. Set up **Customer Statement** and **Automated Action / Cron** for monthly SoA email.  
8. Set up **Follow-up** and escalation to Sales; optional dispute/legal stage.  
9. Optional: Purchase Requisition or internal request from Logistics to Purchasing; reordering rules for stock procurement.  
10. Optional: Slow-moving report and clearance workflow.  
11. Add menus: e.g. “SMB / Credit approval queue”, “SMB / Collection”, and link to standard Sale, Delivery, Invoicing, Purchase.  
12. Document in user guide: who does what at each step (Sales, Credit, Logistics, Purchasing, Inventory, Collection) per SMB-SOP-1.

---

## 6. Optional: Light Extension in ics_tender_management

If you still want a **minimal** touch in ics_tender_management:

- Add a **config** (e.g. on company or tender type): “Send orders from won tenders to SMB credit workflow”.  
- When creating a sale order from a won tender, set default `smb_credit_state = sent_to_credit` (if ics_smb_workflow is installed) so it goes to Credit Control.  
- No full SMB logic inside ics_tender_management; keep the full flow in `ics_smb_workflow`.

---

## 7. Summary

| Question | Answer |
|----------|--------|
| **What is SMB-SOP-1?** | End-to-end SMB flow: Sales (RFQ→Quote→PO) → Credit Control (approve/reject) → Logistics (delivery → invoicing) → Purchasing (procurement) → Inventory (monitoring) → Collection (SoA, follow-up, legal). |
| **New module or extend?** | **New module** `ics_smb_workflow`; optionally depend on ics_tender_management so tender-origin orders use the same SMB flow. |
| **Odoo 18 usage** | Sale (quotation, margin, discount), Stock (delivery, partial), Account (invoicing, credit, statements, follow-up), Purchase (requisition, PO), plus custom states and approvals for Credit Control and Collection escalation. |

This gives you a clear path to implement SMB-SOP-1 in Odoo 18 Enterprise with a dedicated, maintainable module and optional integration with ics_tender_management.
