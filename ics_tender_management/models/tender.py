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
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['ics.tender.stage'].search([], order=order)

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
            'view_mode': 'tree,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_create_purchase_agreement(self):
        self.ensure_one()
        if not self.boq_line_ids:
            raise UserError(_('Please add BoQ lines before creating a purchase agreement.'))

        requisition = self.env['purchase.requisition'].create({
            'tender_id': self.id,
            'user_id': self.user_id.id,
            'ordering_date': fields.Date.today(),
            'schedule_date': self.submission_deadline.date() if self.submission_deadline else False,
            'type_id': self.env.ref('purchase_requisition.type_multi').id,
        })

        for boq_line in self.boq_line_ids:
            self.env['purchase.requisition.line'].create({
                'requisition_id': requisition.id,
                'product_id': boq_line.product_id.id,
                'product_qty': boq_line.quantity,
                'product_uom_id': boq_line.uom_id.id,
                'price_unit': boq_line.estimated_cost / boq_line.quantity if boq_line.quantity else 0,
            })

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
            'view_mode': 'tree,form',
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
            'view_mode': 'tree,form',
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
            'view_mode': 'tree,form',
            'domain': [('tender_id', '=', self.id)],
        }

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', 'ics.tender'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'ics.tender',
                'default_res_id': self.id,
            },
        }

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
