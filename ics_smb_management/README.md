# ICS SMB Management

Odoo 18 module implementing the **SMB Division Standard Operating Procedure (SMB-SOP-1)** for Sales, Credit Control, Logistics, Collection, with **CRM** and **Project** integration (analogy to ics_tender_management).

## Features

### Credit Control (SMB-SOP-1)
- **Credit workflow** on Sale Orders: Draft → Sent to Credit Control → Credit Approved / Rejected
- **Reject with reason** wizard: Credit Control enters reason (e.g. overdue, limit exceeded); Sales uses it to inform the customer
- **Company setting** (Settings → Sales → SMB Credit Control): *Require Credit Approval Before Confirm* (can be disabled per company)
- **Critical order** flag for logistics coordination
- **Credit Approval** menu: queue of quotations pending credit approval
- **Reset credit** after payment clearance so Sales can resubmit

### Collection (SMB-SOP-1)
- **Monthly SoA reminder:** Cron (monthly) creates activities *Send monthly Statement of Account* on partners with receivable balance
- **Escalate overdue to Sales:** Cron (daily) creates activities on overdue invoices assigned to the customer’s salesperson
- **SMB → Overdue Invoices** menu: list of unpaid/partial customer invoices for follow-up

### CRM integration
- **Create SMB Quotation** on Opportunity form: creates a new quotation linked to the opportunity (and partner); quotation goes through SMB credit flow
- Requires **sale_crm** (opportunity_id on sale.order)

### Project integration
- **Create Project** on confirmed Sale Order: wizard to create a **Delivery Project** linked to the order (name, project manager, start date)
- **Project form:** shows linked **Sale Order** and button to open it (same idea as ics_tender_management tender ↔ project)
- **project.project** has `sale_order_id` for delivery/logistics tracking

## Installation

1. Copy `ics_smb_management` into your Odoo addons path.
2. Update the app list and install **ICS SMB Management**.

**Dependencies:** `sale_management`, `stock`, `account`, `crm`, `sale_crm`, `project` (standard Odoo 18).

## Usage

1. **Sales:** Create a quotation (from Opportunity via **Create SMB Quotation** or from Sales) → **Send to Credit**.
2. **Credit Control:** SMB → Credit Approval, or on the quotation → **Approve Credit** or **Reject Credit** (wizard to enter reason).
3. After approval, **Confirm** the order; use **Create Project** for a delivery project if needed.
4. **Collection:** Use SMB → Overdue Invoices; monthly/daily crons create SoA and escalation activities.

## Security

- **SMB Management / User:** SMB fields, Send to Credit, Reset Credit, Create Project, Create SMB Quotation (CRM).
- **SMB Management / Credit Control:** Same + Approve / Reject Credit (and reject wizard).

## Documentation

See `documentation/SMB-SOP-1-Odoo18-Implementation-Guide.md` for the full implementation plan.
