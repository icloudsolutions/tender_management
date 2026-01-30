from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class Tender(models.Model):
    _name = 'ics.tender'
    _description = 'Tender Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char('Tender Reference', required=True, copy=False,
        readonly=True, default=lambda self: _('New'))

    etimad_tender_id = fields.Many2one('ics.etimad.tender', string='Etimad Tender',
        help='Link to the scraped tender from Etimad portal')

    lead_id = fields.Many2one('crm.lead', string='CRM Lead/Opportunity',
        tracking=True, ondelete='restrict')

    partner_id = fields.Many2one('res.partner', string='Customer',
        tracking=True, required=True)

    tender_number = fields.Char('Tender Number', required=True, tracking=True,
        help='Official tender number from Etimad or customer')

    tender_title = fields.Char('Tender Title', required=True, tracking=True)

    tender_category = fields.Selection([
        ('supply', 'Supply'),
        ('services', 'Services'),
        ('construction', 'Construction'),
        ('maintenance', 'Maintenance & Operation'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ], string='Tender Category', required=True, tracking=True)

    tender_type = fields.Selection([
        ('single_vendor', 'Single Vendor for All Products'),
        ('product_wise', 'Product-wise Vendor Selection'),
    ], string='Tender Type', default='single_vendor', required=True, tracking=True,
        help='Single Vendor: Select one vendor for all products (all prices mandatory). '
             'Product-wise: Select different vendors per product (prices optional, multiple POs).')

    description = fields.Html('Description')

    stage_id = fields.Many2one('ics.tender.stage', string='Stage',
        tracking=True, ondelete='restrict', group_expand='_read_group_stage_ids',
        default=lambda self: self.env['ics.tender.stage'].search([], limit=1))

    active = fields.Boolean('Active', default=True)

    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.company)

    currency_id = fields.Many2one('res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)

    user_id = fields.Many2one('res.users', string='Responsible',
        default=lambda self: self.env.user, tracking=True)

    team_id = fields.Many2one('crm.team', string='Sales Team')

    announcement_date = fields.Date('Announcement Date', tracking=True)
    document_purchase_date = fields.Date('Purchase Documents Date', tracking=True)
    submission_deadline = fields.Datetime('Submission Deadline', required=True, tracking=True)
    opening_date = fields.Datetime('Opening Date', tracking=True)

    days_to_deadline = fields.Integer('Days to Deadline', compute='_compute_days_to_deadline')
    is_urgent = fields.Boolean('Urgent', compute='_compute_is_urgent', store=True)

    boq_line_ids = fields.One2many('ics.tender.boq.line', 'tender_id',
        string='Bill of Quantities Lines')
    boq_count = fields.Integer('BoQ Lines', compute='_compute_boq_count')

    total_estimated_cost = fields.Monetary('Total Estimated Cost',
        compute='_compute_totals', store=True, currency_field='currency_id')
    total_vendor_cost = fields.Monetary('Total Vendor Cost',
        compute='_compute_totals', store=True, currency_field='currency_id')
    margin_amount = fields.Monetary('Margin Amount',
        compute='_compute_totals', store=True, currency_field='currency_id')
    margin_percentage = fields.Float('Margin %', default=20.0, tracking=True)
    total_quotation_amount = fields.Monetary('Total Quotation Amount',
        compute='_compute_totals', store=True, currency_field='currency_id')

    requisition_ids = fields.One2many('purchase.requisition', 'tender_id',
        string='Purchase Agreements (RFQs)')
    requisition_count = fields.Integer('Purchase Agreements', compute='_compute_requisition_count')

    quotation_ids = fields.One2many('sale.order', 'tender_id', string='Quotations')
    quotation_count = fields.Integer('Quotations', compute='_compute_quotation_count')

    project_ids = fields.One2many('project.project', 'tender_id', string='Projects')
    project_count = fields.Integer('Projects', compute='_compute_project_count')

    notes = fields.Html('Internal Notes')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('technical', 'Technical Study'),
        ('financial', 'Financial Study'),
        ('quotation', 'Quotation Prepared'),
        ('submitted', 'Submitted'),
        ('evaluation', 'Under Evaluation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)

    color = fields.Integer('Color Index')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1')

    tag_ids = fields.Many2many('crm.tag', string='Tags')

    attachment_count = fields.Integer('Attachments', compute='_compute_attachment_count')

    winning_reason = fields.Text('Winning Reason')
    lost_reason = fields.Text('Lost Reason')

    expected_revenue = fields.Monetary('Expected Revenue', currency_field='currency_id')
    actual_revenue = fields.Monetary('Actual Revenue', currency_field='currency_id')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ics.tender') or _('New')
        return super(Tender, self).create(vals)

    @api.depends('submission_deadline')
    def _compute_days_to_deadline(self):
        today = fields.Datetime.now()
        for tender in self:
            if tender.submission_deadline:
                delta = tender.submission_deadline - today
                tender.days_to_deadline = delta.days
            else:
                tender.days_to_deadline = 0

    @api.depends('days_to_deadline')
    def _compute_is_urgent(self):
        for tender in self:
            tender.is_urgent = tender.days_to_deadline <= 7 and tender.days_to_deadline >= 0

    @api.depends('boq_line_ids')
    def _compute_boq_count(self):
        for tender in self:
            tender.boq_count = len(tender.boq_line_ids)

    @api.depends('boq_line_ids.estimated_cost', 'boq_line_ids.selected_vendor_price', 'margin_percentage')
    def _compute_totals(self):
        for tender in self:
            tender.total_estimated_cost = sum(tender.boq_line_ids.mapped('estimated_cost'))
            tender.total_vendor_cost = sum(tender.boq_line_ids.mapped('selected_vendor_price'))

            if tender.total_vendor_cost > 0:
                tender.margin_amount = tender.total_vendor_cost * (tender.margin_percentage / 100)
                tender.total_quotation_amount = tender.total_vendor_cost + tender.margin_amount
            else:
                tender.margin_amount = 0
                tender.total_quotation_amount = 0

    @api.depends('requisition_ids')
    def _compute_requisition_count(self):
        for tender in self:
            tender.requisition_count = len(tender.requisition_ids)

    @api.depends('quotation_ids')
    def _compute_quotation_count(self):
        for tender in self:
            tender.quotation_count = len(tender.quotation_ids)

    @api.depends('project_ids')
    def _compute_project_count(self):
        for tender in self:
            tender.project_count = len(tender.project_ids)

    def _compute_attachment_count(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'ics.tender'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for tender in self:
            tender.attachment_count = attachment.get(tender.id, 0)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Odoo 18: group_expand no longer receives 'order' parameter"""
        return self.env['ics.tender.stage'].search([], order='sequence, id')

    def action_start_technical_study(self):
        self.ensure_one()
        self.write({'state': 'technical'})

    def action_start_financial_study(self):
        self.ensure_one()
        if not self.boq_line_ids:
            raise UserError(_('Please add BoQ lines before starting financial study.'))
        self.write({'state': 'financial'})

    def action_prepare_quotation(self):
        self.ensure_one()
        if not self.boq_line_ids:
            raise UserError(_('Please add BoQ lines before preparing quotation.'))
        self.write({'state': 'quotation'})

    def action_submit_tender(self):
        self.ensure_one()
        if not self.quotation_ids:
            raise UserError(_('Please generate a quotation before submitting the tender.'))
        self.write({'state': 'submitted'})

    def action_mark_won(self):
        self.ensure_one()
        self.write({'state': 'won'})
        if self.lead_id:
            self.lead_id.action_set_won()

    def action_mark_lost(self):
        self.ensure_one()
        return {
            'name': _('Lost Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_state': 'lost'},
        }

    def action_view_boq_lines(self):
        self.ensure_one()
        return {
            'name': _('Bill of Quantities'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.boq.line',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_create_purchase_agreement(self):
        self.ensure_one()
        if not self.boq_line_ids:
            raise UserError(_('Please add BoQ lines before creating a purchase agreement.'))

        # Try to get the purchase requisition type, fallback gracefully if not found
        type_id = False
        try:
            type_id = self.env.ref('purchase_requisition.type_multi').id
        except (ValueError, KeyError):
            # Odoo 18: type_multi might not exist, try to get any blanket order type
            # Check if the model exists first
            if 'purchase.requisition.type' in self.env:
                type_obj = self.env['purchase.requisition.type'].search([('name', 'ilike', 'blanket')], limit=1)
                type_id = type_obj.id if type_obj else False

        # Build vals dict with only fields that exist in the model
        requisition_model = self.env['purchase.requisition']
        available_fields = requisition_model._fields.keys()
        
        vals = {}
        
        # Add tender_id if field exists
        if 'tender_id' in available_fields:
            vals['tender_id'] = self.id
            
        # Add user_id if field exists
        if 'user_id' in available_fields:
            vals['user_id'] = self.user_id.id
            
        # Add ordering_date if field exists (might not exist in some versions)
        if 'ordering_date' in available_fields:
            vals['ordering_date'] = fields.Date.today()
            
        # Add schedule_date if field exists
        if 'schedule_date' in available_fields and self.submission_deadline:
            vals['schedule_date'] = self.submission_deadline.date()
        
        # Add type_id if we found one
        if type_id and 'type_id' in available_fields:
            vals['type_id'] = type_id

        requisition = requisition_model.create(vals)

        # Create requisition lines from BoQ
        line_model = self.env['purchase.requisition.line']
        line_fields = line_model._fields.keys()
        
        for boq_line in self.boq_line_ids:
            line_vals = {
                'requisition_id': requisition.id,
                'product_id': boq_line.product_id.id,
            }
            
            # Add optional fields if they exist
            if 'product_qty' in line_fields:
                line_vals['product_qty'] = boq_line.quantity
            if 'product_uom_id' in line_fields:
                line_vals['product_uom_id'] = boq_line.uom_id.id
            if 'price_unit' in line_fields:
                line_vals['price_unit'] = boq_line.estimated_cost / boq_line.quantity if boq_line.quantity else 0
                
            line_model.create(line_vals)

        return {
            'name': _('Purchase Agreement'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'view_mode': 'form',
            'res_id': requisition.id,
            'target': 'current',
        }

    def action_view_purchase_agreements(self):
        self.ensure_one()
        return {
            'name': _('Purchase Agreements'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_generate_quotation(self):
        self.ensure_one()
        return {
            'name': _('Generate Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.quotation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'name': _('Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id, 'default_partner_id': self.partner_id.id},
        }

    def action_compare_vendors(self):
        self.ensure_one()
        return {
            'name': _('Compare Vendor Offers'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.vendor.comparison.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }

    def action_create_project(self):
        self.ensure_one()
        if self.state != 'won':
            raise UserError(_('You can only create a project for won tenders.'))

        return {
            'name': _('Create Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }

    def action_view_projects(self):
        self.ensure_one()
        return {
            'name': _('Projects'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
        }

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', 'ics.tender'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'ics.tender',
                'default_res_id': self.id,
            },
        }

    def action_create_purchase_orders(self):
        self.ensure_one()

        if self.tender_type == 'single_vendor':
            return self._create_single_purchase_order()
        else:
            return self._create_multiple_purchase_orders()

    def _create_single_purchase_order(self):
        missing_selections = self.boq_line_ids.filtered(lambda l: not l.selected_vendor_id)
        if missing_selections:
            raise UserError(_(
                'Single Vendor Mode requires all products to be assigned to vendors.\n'
                'Missing vendor selection for: %s'
            ) % ', '.join(missing_selections.mapped('name')))

        vendors = self.boq_line_ids.mapped('selected_vendor_id')
        if len(vendors) > 1:
            raise UserError(_(
                'Single Vendor Mode requires all products to use the same vendor.\n'
                'Currently selected vendors: %s'
            ) % ', '.join(vendors.mapped('name')))

        if not vendors:
            raise UserError(_('Please select a vendor for the products.'))

        vendor = vendors[0]

        # Build purchase order vals with only available fields
        po_model = self.env['purchase.order']
        po_fields = po_model._fields.keys()
        
        po_vals = {'partner_id': vendor.id}
        
        if 'tender_id' in po_fields:
            po_vals['tender_id'] = self.id
        if 'origin' in po_fields:
            po_vals['origin'] = self.name
        if 'date_order' in po_fields:
            po_vals['date_order'] = fields.Datetime.now()
            
        purchase_order = po_model.create(po_vals)

        # Build purchase order line vals with only available fields
        pol_model = self.env['purchase.order.line']
        pol_fields = pol_model._fields.keys()
        
        for boq_line in self.boq_line_ids:
            pol_vals = {
                'order_id': purchase_order.id,
                'product_id': boq_line.product_id.id,
            }
            
            if 'name' in pol_fields:
                pol_vals['name'] = boq_line.name
            if 'product_qty' in pol_fields:
                pol_vals['product_qty'] = boq_line.quantity
            if 'product_uom' in pol_fields:
                pol_vals['product_uom'] = boq_line.uom_id.id
            if 'price_unit' in pol_fields:
                pol_vals['price_unit'] = boq_line.selected_vendor_price / boq_line.quantity if boq_line.quantity else 0
            if 'date_planned' in pol_fields:
                pol_vals['date_planned'] = fields.Datetime.now()
                
            pol_model.create(pol_vals)

        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
            'target': 'current',
        }

    def _create_multiple_purchase_orders(self):
        lines_with_vendor = self.boq_line_ids.filtered(lambda l: l.selected_vendor_id)

        if not lines_with_vendor:
            raise UserError(_('Please select vendors for at least one product.'))

        vendors = lines_with_vendor.mapped('selected_vendor_id')
        created_orders = self.env['purchase.order']
        
        # Get available fields once to avoid repeated lookups
        po_model = self.env['purchase.order']
        po_fields = po_model._fields.keys()
        pol_model = self.env['purchase.order.line']
        pol_fields = pol_model._fields.keys()

        for vendor in vendors:
            vendor_lines = lines_with_vendor.filtered(lambda l: l.selected_vendor_id == vendor)

            # Build purchase order vals with only available fields
            po_vals = {'partner_id': vendor.id}
            
            if 'tender_id' in po_fields:
                po_vals['tender_id'] = self.id
            if 'origin' in po_fields:
                po_vals['origin'] = self.name
            if 'date_order' in po_fields:
                po_vals['date_order'] = fields.Datetime.now()
                
            purchase_order = po_model.create(po_vals)

            # Build purchase order line vals with only available fields
            for boq_line in vendor_lines:
                pol_vals = {
                    'order_id': purchase_order.id,
                    'product_id': boq_line.product_id.id,
                }
                
                if 'name' in pol_fields:
                    pol_vals['name'] = boq_line.name
                if 'product_qty' in pol_fields:
                    pol_vals['product_qty'] = boq_line.quantity
                if 'product_uom' in pol_fields:
                    pol_vals['product_uom'] = boq_line.uom_id.id
                if 'price_unit' in pol_fields:
                    pol_vals['price_unit'] = boq_line.selected_vendor_price / boq_line.quantity if boq_line.quantity else 0
                if 'date_planned' in pol_fields:
                    pol_vals['date_planned'] = fields.Datetime.now()
                    
                pol_model.create(pol_vals)

            created_orders |= purchase_order

        if len(created_orders) == 1:
            return {
                'name': _('Purchase Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': created_orders.id,
                'target': 'current',
            }
        else:
            return {
                'name': _('Purchase Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'list,form',
                'domain': [('id', 'in', created_orders.ids)],
                'target': 'current',
            }

    def _validate_vendor_selection(self):
        self.ensure_one()

        if self.tender_type == 'single_vendor':
            missing_selections = self.boq_line_ids.filtered(lambda l: not l.selected_vendor_id)
            if missing_selections:
                raise ValidationError(_(
                    'Single Vendor Mode: All products must have a vendor selected.\n'
                    'Missing selections for: %s'
                ) % ', '.join(missing_selections.mapped('name')))

            vendors = self.boq_line_ids.mapped('selected_vendor_id')
            if len(vendors) > 1:
                raise ValidationError(_(
                    'Single Vendor Mode: All products must use the same vendor.\n'
                    'Please select only one vendor for all products.'
                ))

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            self.partner_id = self.lead_id.partner_id
            self.tender_title = self.lead_id.name
            self.user_id = self.lead_id.user_id
            self.team_id = self.lead_id.team_id
            self.expected_revenue = self.lead_id.expected_revenue

    @api.onchange('etimad_tender_id')
    def _onchange_etimad_tender_id(self):
        if self.etimad_tender_id:
            self.tender_number = self.etimad_tender_id.tender_number
            self.tender_title = self.etimad_tender_id.tender_title
            self.announcement_date = self.etimad_tender_id.announcement_date
            self.submission_deadline = self.etimad_tender_id.submission_deadline
