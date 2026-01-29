# ICS Tender Management - Technical Documentation

## Module Architecture

### 1. Core Models

#### ics.tender (Main Tender Model)
The central model for managing tenders throughout their lifecycle.

**Key Fields:**
- `name`: Tender reference (auto-generated: TND/00001)
- `etimad_tender_id`: Link to scraped Etimad tender
- `lead_id`: CRM lead/opportunity link
- `partner_id`: Customer
- `tender_number`: Official tender number
- `tender_title`: Tender title
- `tender_category`: Supply, Services, Construction, Maintenance, Consulting, Other
- `stage_id`: Kanban stage
- `state`: Workflow state (draft → technical → financial → quotation → submitted → evaluation → won/lost)
- `submission_deadline`: Deadline for submission
- `boq_line_ids`: Bill of Quantities lines
- `requisition_ids`: Purchase Agreements (RFQs)
- `quotation_ids`: Sales quotations
- `project_ids`: Related projects

**Financial Fields:**
- `total_estimated_cost`: Sum of estimated costs from BoQ
- `total_vendor_cost`: Sum of selected vendor prices
- `margin_percentage`: Configurable margin %
- `margin_amount`: Calculated margin
- `total_quotation_amount`: Final quotation amount

**Computed Fields:**
- `days_to_deadline`: Days remaining until submission
- `is_urgent`: True if deadline within 7 days
- `boq_count`, `requisition_count`, `quotation_count`, `project_count`

#### ics.tender.stage
Kanban stages for visual workflow management.

**Default Stages:**
1. Draft
2. Technical Study
3. Financial Study
4. Quotation Prepared
5. Submitted
6. Under Evaluation
7. Won
8. Lost
9. Cancelled

#### ics.tender.boq.line
Bill of Quantities line items.

**Key Fields:**
- `tender_id`: Parent tender
- `product_id`: Product/service
- `name`: Description
- `quantity`: Quantity
- `uom_id`: Unit of measure
- `estimated_cost`: Initial cost estimate
- `vendor_offer_ids`: Vendor offers for this line
- `selected_vendor_id`: Chosen vendor
- `selected_vendor_price`: Selected vendor's total price
- `specifications`: Technical specifications (HTML)

#### ics.tender.vendor.offer
Individual vendor offers for BoQ lines.

**Key Fields:**
- `boq_line_id`: Related BoQ line
- `vendor_id`: Vendor/supplier
- `unit_price`: Price per unit
- `total_price`: Computed total (unit_price × quantity)
- `delivery_lead_time`: Delivery time in days
- `payment_terms`: Payment terms
- `is_selected`: Computed - true if this vendor is selected

### 2. Integration Models

#### crm.lead (Extended)
**Added Fields:**
- `tender_ids`: Related tenders
- `tender_count`: Number of tenders
- `etimad_tender_id`: Link to Etimad tender

**New Actions:**
- `action_view_tenders()`: View all tenders for this lead
- `action_create_tender()`: Create new tender from opportunity

#### purchase.requisition (Extended)
**Added Fields:**
- `tender_id`: Related tender

**New Actions:**
- `action_view_tender()`: Navigate to related tender

#### sale.order (Extended)
**Added Fields:**
- `tender_id`: Related tender

**New Actions:**
- `action_view_tender()`: Navigate to related tender

#### project.project (Extended)
**Added Fields:**
- `tender_id`: Related tender
- `sale_order_id`: Related sales order

**New Actions:**
- `action_view_tender()`: Navigate to related tender
- `action_view_sale_order()`: Navigate to sales order

### 3. Wizards

#### ics.tender.vendor.comparison.wizard
Compare vendor offers side-by-side.

**Features:**
- Displays all BoQ lines with best vendor offers
- Calculates savings vs. estimated costs
- Shows number of offers per line
- One-click application of best vendors

**Line Model: ics.tender.vendor.comparison.line**
- Shows product, quantity, estimated cost
- Best vendor and their pricing
- Calculated savings (amount and percentage)
- Link to view all offers for the line

#### ics.tender.quotation.wizard
Generate sales quotations with margin calculation.

**Features:**
- Configure margin percentage
- Choose between vendor costs or estimated costs
- Preview all quotation lines before creation
- Set pricelist, payment terms, validity date
- Add terms and conditions

**Line Model: ics.tender.quotation.line.preview**
- Shows cost, margin, unit price, total for each line
- Totals: cost, margin, final amount

#### ics.tender.project.wizard
Create projects from won tenders.

**Features:**
- Set project name and manager
- Link to confirmed sales order
- Option to create tasks from BoQ lines
- Configure start date

### 4. Security

**Groups:**
- `group_tender_user`: Basic tender users
  - Create and edit own tenders
  - View all tenders
  - Cannot delete tenders

- `group_tender_manager`: Tender managers
  - Full access to all tenders
  - Manage stages and configuration
  - Delete tenders

**Record Rules:**
- Users can only modify their own tenders
- Managers have full access

### 5. Workflows

#### A. Tender Creation Workflow

1. **From Etimad Scraper:**
   - Etimad tender scraped → CRM lead created
   - User opens lead → Click "Create Tender"
   - Tender auto-populated with Etimad data

2. **Manual Creation:**
   - Navigate to Tender Management → Create
   - Fill tender details manually
   - Optionally link to existing CRM opportunity

#### B. Technical & Financial Study Workflow

1. **Technical Study:**
   - Click "Start Technical Study" button
   - Upload and review tender documents
   - Analyze technical requirements
   - Add BoQ lines with products and specifications

2. **Financial Study:**
   - Click "Start Financial Study"
   - System validates BoQ lines exist
   - Click "Create RFQ (Purchase Agreement)"
   - System creates Purchase Agreement with all BoQ items
   - Send RFQs to multiple vendors
   - Vendors submit quotations
   - Vendor offers automatically linked to BoQ lines

3. **Vendor Comparison:**
   - Click "Compare Vendors" button
   - Wizard shows best offers per line
   - Review savings and alternatives
   - Click "Apply Best Vendors"
   - Selected vendors updated on BoQ lines

#### C. Quotation Generation Workflow

1. **Prepare Quotation:**
   - Click "Prepare Quotation" button
   - State changes to 'quotation'

2. **Generate Sales Quotation:**
   - Click "Generate Sales Quotation"
   - Wizard opens with configuration:
     - Set margin percentage (default 20%)
     - Choose cost source (vendor/estimated)
     - Set pricelist and payment terms
     - Preview all lines with costs and margins
   - Click "Generate Quotation"
   - Sales order created with all items
   - Tender state updated

3. **Submit Tender:**
   - Review generated quotation
   - Click "Submit Tender"
   - State changes to 'submitted'

#### D. Evaluation & Award Workflow

1. **Under Evaluation:**
   - Manually move to "Under Evaluation" stage
   - Track customer evaluation process
   - Update notes and activities

2. **Won:**
   - Click "Mark as Won"
   - State changes to 'won'
   - Related CRM opportunity also marked won
   - "Create Project" button appears

3. **Lost:**
   - Click "Mark as Lost"
   - Enter lost reason
   - State changes to 'lost'
   - Archive option available

#### E. Project Creation Workflow

1. **Create Project:**
   - Click "Create Project" (only visible for won tenders)
   - Wizard opens:
     - Set project name (auto-filled)
     - Select project manager
     - Choose related sales order
     - Enable "Create Tasks from BoQ"
   - Click "Create Project"
   - Project created with:
     - Customer information
     - Sales order link (if selected)
     - Tasks from each BoQ line (if enabled)
     - Each task includes specifications

### 6. Reports

#### Tender Report
Comprehensive tender overview including:
- Tender details and customer
- Submission deadline and status
- Description
- Financial summary with costs, margin, total

#### Tender BoQ Report
Detailed Bill of Quantities with:
- Item numbering
- Product descriptions
- Quantities and units
- Unit prices and totals
- Grand total

### 7. Best Practices

#### For Users:

1. **Always start from CRM:**
   - Create lead from Etimad scraper
   - Convert to opportunity
   - Create tender from opportunity

2. **Complete BoQ before RFQs:**
   - Add all products to BoQ
   - Set quantities accurately
   - Add technical specifications

3. **Use vendor comparison:**
   - Don't manually select vendors
   - Use comparison wizard for best analysis
   - Review savings before applying

4. **Configure margins properly:**
   - Consider overhead costs
   - Account for risk factors
   - Review preview before generating

5. **Document everything:**
   - Use chatter for communication
   - Schedule activities for follow-ups
   - Attach all tender documents

#### For Administrators:

1. **Configure stages:**
   - Customize to match company workflow
   - Add requirements to each stage
   - Set fold/unfold appropriately

2. **Set up teams:**
   - Assign users to sales teams
   - Configure team-based access
   - Set up team targets

3. **Create products:**
   - Maintain product catalog
   - Set accurate costs
   - Add detailed descriptions

4. **Train vendors:**
   - Ensure vendors can access portal
   - Provide RFQ submission guidelines
   - Set up vendor contacts

### 8. Integration Points

#### With ics_etimad_tenders_crm:
- Automatic tender scraping
- Lead creation from Etimad
- Tender data synchronization

#### With CRM:
- Opportunity to tender conversion
- Expected revenue tracking
- Win/loss synchronization

#### With Purchase:
- Purchase Agreement creation
- Vendor RFQ management
- Quotation collection

#### With Sales:
- Sales quotation generation
- Order confirmation
- Revenue recognition

#### With Project:
- Automatic project creation
- Task generation from BoQ
- Sales order integration

### 9. Customization Guide

#### Adding Custom Fields:

```python
class Tender(models.Model):
    _inherit = 'ics.tender'

    custom_field = fields.Char('Custom Field')
```

#### Adding Custom Stages:

Navigate to: Tender Management > Configuration > Tender Stages
Click Create and add your stage.

#### Modifying Workflows:

Override button actions:

```python
def action_custom_workflow(self):
    self.ensure_one()
    # Your custom logic
    return super(Tender, self).action_custom_workflow()
```

#### Adding Custom Reports:

Create new report template in `report/` directory.

### 10. Troubleshooting

**Issue: Can't create tender from CRM**
- Ensure ics_etimad_tenders_crm is installed
- Check user has tender user group
- Verify CRM opportunity exists

**Issue: Purchase Agreement not creating**
- Check BoQ lines exist
- Verify Purchase Requisition module installed
- Check user permissions

**Issue: Quotation not generating**
- Ensure BoQ has products
- Check if vendor costs selected
- Verify Sales Management installed

**Issue: Project creation fails**
- Verify tender is in 'won' state
- Check Project module installed
- Ensure user has project access

### 11. API Reference

#### Create Tender:
```python
tender = env['ics.tender'].create({
    'partner_id': partner_id,
    'tender_number': 'TND-001',
    'tender_title': 'Supply Contract',
    'tender_category': 'supply',
    'submission_deadline': '2024-12-31',
})
```

#### Add BoQ Line:
```python
boq_line = env['ics.tender.boq.line'].create({
    'tender_id': tender.id,
    'product_id': product.id,
    'name': 'Product description',
    'quantity': 100,
    'uom_id': uom.id,
    'estimated_cost': 10000,
})
```

#### Create Purchase Agreement:
```python
tender.action_create_purchase_agreement()
```

#### Generate Quotation:
```python
wizard = env['ics.tender.quotation.wizard'].create({
    'tender_id': tender.id,
    'margin_percentage': 25,
})
wizard.action_generate_quotation()
```

### 12. Support and Contact

For implementation support, customization, or questions:

**iCloud Solutions**
- Website: https://icloud-solutions.net
- Email: contact@icloud-solutions.net
- WhatsApp: +216 50 271 737

---

**Module Version:** 18.0.1.0.0
**License:** OPL-1
**Author:** iCloud Solutions
