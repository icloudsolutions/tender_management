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
        tracking=True, required=False)

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

    # ========== LEGACY CRM MIGRATION FIELDS ==========
    # Tendering Details
    etimad_link = fields.Char('Etimad Tender Link', help='URL to the tender on Etimad portal')
    tender_completion_time = fields.Integer('Tender Completion Time (Months)', help='Expected project duration in months')
    tender_submission_method = fields.Selection([
        ('electronic', 'Electronic'),
        ('manual', 'Manual'),
        ('both', 'Both')
    ], string='Submission Method', default='electronic')
    tender_booklet_price = fields.Monetary('Tender Booklet Price', currency_field='currency_id')
    
    # Booklet Purchase Details
    booklet_purchased = fields.Boolean('Booklet Purchased?', default=False)
    booklet_purchase_receipt = fields.Char('Purchase Receipt Number')
    booklet_purchase_request_date = fields.Date('Date of Booklet Purchase Request')
    booklet_purchase_date = fields.Date('Date of Purchase')
    
    # Site Visit & Inquiries
    site_visit_required = fields.Boolean('Site Visit Required', default=False)
    site_visit_date = fields.Datetime('Site Visit Date')
    last_inquiry_date = fields.Date('Last Date for Inquiries')
    
    # Offer Opening Dates
    offer_opening_date = fields.Datetime('Offer Opening Date')
    financial_offer_opening_date = fields.Datetime('Financial Offer Opening Date')
    
    # Competing Companies & Prices
    competing_companies_file = fields.Binary('Upload Competing Companies Prices')
    competing_companies_filename = fields.Char('Competing Companies File Name')
    
    # Offer Acceptance/Rejection
    offer_accepted = fields.Boolean('Offer Accepted', default=False)
    offer_rejection_reason = fields.Text('Reasons for Offer Rejection')
    financial_offer_accepted = fields.Boolean('Financial Offer Accepted', default=False)
    financial_offer_rejection_reason = fields.Text('Reason for Rejected Financial Offer')
    
    # Extensions & Appeals
    offer_extension_requested = fields.Boolean('Offer Extension', default=False)
    extension_awarded = fields.Boolean('Extension Awarded', default=False)
    extension_rejection_reason = fields.Text('Reason for Extension Rejected')
    discount_requested = fields.Boolean('Discount Requested', default=False)
    appeal_submitted = fields.Boolean('Appeal Submitted', default=False)
    appeal_submission_date = fields.Date('Appeal Submission Date')
    appeal_letter_file = fields.Binary('Appeal Letter')
    appeal_letter_filename = fields.Char('Appeal Letter Filename')
    appeal_reason = fields.Text('Appeal Reason')
    appeal_status = fields.Selection([
        ('pending', 'Pending Response'),
        ('accepted', 'Appeal Accepted'),
        ('rejected', 'Appeal Rejected'),
        ('withdrawn', 'Withdrawn')
    ], string='Appeal Status')
    appeal_response_date = fields.Date('Appeal Response Date')
    appeal_response_notes = fields.Text('Appeal Response Notes')
    
    # Award Details
    awarded_company = fields.Many2one('res.partner', string='Awarded Company')
    amount_awarded = fields.Monetary('Amount Awarded', currency_field='currency_id')
    award_date = fields.Date('Date Awarded')
    award_letter_file = fields.Binary('Upload Award Letter')
    award_letter_filename = fields.Char('Award Letter File Name')
    
    # Approvals
    approval_direct_manager = fields.Boolean('Approval from Direct Manager', default=False)
    approval_department_manager = fields.Boolean('Approval from Department Manager', default=False)
    approval_financial_manager = fields.Boolean('Approval from Financial Manager', default=False)
    approval_ceo = fields.Boolean('CEO Approval', default=False)
    
    # Qualification Phase
    presales_employee = fields.Many2one('res.users', string='Presales Employee')
    evaluation_criteria_file = fields.Binary('Evaluation Criteria')
    evaluation_criteria_filename = fields.Char('Evaluation Criteria File Name')
    required_certifications_file = fields.Binary('Required Certifications')
    required_certifications_filename = fields.Char('Required Certifications File Name')
    project_scope_of_work = fields.Html('Project Scope of Work')
    estimated_project_value = fields.Monetary('Estimated Project Value', currency_field='currency_id')
    required_inquiries = fields.Text('Required Inquiries/Questions')
    
    # Evaluation Phase
    challenges = fields.Text('Challenges')
    winning_probability = fields.Float('Winning Probability', help='Probability percentage (0-100)')
    client_relationship = fields.Selection([
        ('new', 'New Client'),
        ('existing', 'Existing Client'),
        ('strategic', 'Strategic Partner')
    ], string='Client Relationship')
    participation_decision = fields.Boolean('Participating in Tender', default=True)
    non_participation_reason = fields.Text('Reasons for Non-Participation')
    
    # Document Management
    tender_documents_uploaded = fields.Boolean('Update Tender Documents', default=False)
    documents_required_for_site = fields.Binary('Documents Required For Site Visit')
    documents_required_filename = fields.Char('Documents Required File Name')
    file_submission_required = fields.Boolean('File Submission', default=False)
    file_submission_date = fields.Date('Final Time and Date for Final Offers Approval')
    documents_upload_for_review = fields.Binary('Document Upload for Review')
    documents_upload_filename = fields.Char('Documents Upload File Name')
    
    # Communication Team
    tender_team_ids = fields.One2many('ics.tender.team', 'tender_id', string='Tender Communication Team')
    tender_employee = fields.Many2one('res.users', string='Tender Employee')
    sales_representative = fields.Many2one('res.users', string='Sales Representative')
    
    # Supplier Selection
    selected_suppliers_ids = fields.Many2many('res.partner', 'tender_supplier_rel', 
        'tender_id', 'partner_id', string='Selected Suppliers', 
        domain=[('supplier_rank', '>', 0)])
    potential_suppliers_ids = fields.One2many('ics.tender.supplier', 'tender_id', 
        string='Potential Suppliers')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ics.tender') or _('New')
        return super(Tender, self).create(vals)
    
    def write(self, vals):
        """Auto-create project when tender is won & sync CRM stages & trigger activities"""
        old_states = {tender.id: tender.state for tender in self}
        
        res = super(Tender, self).write(vals)
        
        # Trigger activities when state changes
        if vals.get('state'):
            for tender in self:
                old_state = old_states.get(tender.id)
                if old_state != tender.state:
                    tender._trigger_state_activities(old_state, tender.state)
                
                # Sync CRM opportunity stage
                if tender.lead_id:
                    tender._sync_crm_stage()
        
        # Auto-create project when tender becomes 'won'
        if vals.get('state') == 'won':
            for tender in self:
                # Check if project already exists
                if tender.project_count > 0:
                    continue
                
                # Auto-create project with task template
                tender._auto_create_project()
        
        # Trigger appeal workflow when tender is lost
        if vals.get('state') == 'lost':
            for tender in self:
                tender._trigger_appeal_option()
        
        # Handle site visit requirement
        if vals.get('site_visit_required') and vals['site_visit_required']:
            for tender in self:
                tender._schedule_site_visit_activity()
        
        return res
    
    def _sync_crm_stage(self):
        """Synchronize tender state to CRM opportunity stage"""
        self.ensure_one()
        
        if not self.lead_id:
            return
        
        # Map tender states to CRM stages
        stage_mapping = self._get_crm_stage_mapping()
        
        crm_stage_name = stage_mapping.get(self.state)
        if not crm_stage_name:
            return
        
        # Find CRM stage
        crm_stage = self.env['crm.stage'].search([
            ('name', '=ilike', crm_stage_name)
        ], limit=1)
        
        if not crm_stage:
            # Try to find by partial match
            for stage_name in [crm_stage_name, crm_stage_name.split()[0]]:
                crm_stage = self.env['crm.stage'].search([
                    ('name', 'ilike', stage_name)
                ], limit=1)
                if crm_stage:
                    break
        
        if crm_stage:
            # Update CRM opportunity with context to bypass lock
            self.lead_id.with_context(from_tender_sync=True).write({
                'stage_id': crm_stage.id,
                'probability': self._get_crm_probability(),
            })
            
            # Log the sync in CRM
            self.lead_id.message_post(
                body=_('Stage synchronized from Tender: <a href="/web#id=%s&model=ics.tender">%s</a><br/>Tender State: %s') % (
                    self.id, self.name, dict(self._fields['state'].selection).get(self.state)
                ),
                subject=_('Tender Stage Update')
            )
    
    def _get_crm_stage_mapping(self):
        """Map tender states to CRM stage names"""
        return {
            'draft': 'New',  # or 'Qualification'
            'technical': 'Qualified',  # Technical analysis phase
            'financial': 'Proposition',  # Financial offer preparation
            'quotation': 'Proposition',  # Quotation ready
            'submitted': 'Proposition',  # Submitted to customer
            'evaluation': 'Negotiation',  # Under customer evaluation
            'won': 'Won',  # Tender won
            'lost': 'Lost',  # Tender lost
            'cancelled': 'Lost',  # Cancelled
        }
    
    def _get_crm_probability(self):
        """Get probability based on tender state"""
        probability_mapping = {
            'draft': 5,
            'technical': 20,
            'financial': 40,
            'quotation': 60,
            'submitted': 75,
            'evaluation': 85,
            'won': 100,
            'lost': 0,
            'cancelled': 0,
        }
        return probability_mapping.get(self.state, 20)
    
    def _auto_create_project(self):
        """Automatically create project from won tender with task template"""
        self.ensure_one()
        
        # Find appropriate task template based on tender category
        template = self.env['ics.project.task.template'].search([
            ('tender_category', '=', self.tender_category),
            ('active', '=', True)
        ], limit=1)
        
        # If no category-specific template, get general template
        if not template:
            template = self.env['ics.project.task.template'].search([
                ('tender_category', '=', False),
                ('active', '=', True)
            ], limit=1)
        
        # Create project
        project_vals = {
            'name': f"Project - {self.tender_title}",
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'tender_id': self.id,
            'date_start': fields.Date.today(),
        }
        
        # Link to sales order if exists
        confirmed_order = self.env['sale.order'].search([
            ('tender_id', '=', self.id),
            ('state', 'in', ['sale', 'done'])
        ], limit=1)
        if confirmed_order:
            project_vals['sale_order_id'] = confirmed_order.id
        
        project = self.env['project.project'].create(project_vals)
        
        # Create tasks from template
        if template and template.task_line_ids:
            from datetime import timedelta
            project_start = fields.Date.today()
            
            # Check available fields on project.task for version compatibility
            task_model = self.env['project.task']
            available_task_fields = task_model._fields.keys()
            
            for line in template.task_line_ids:
                task_vals = {
                    'name': line.name,
                    'project_id': project.id,
                    'partner_id': self.partner_id.id,
                    'description': line.description,
                    'priority': line.priority,
                    'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                }
                
                # Add planned_hours field if available (field name may vary by Odoo version)
                if 'planned_hours' in available_task_fields:
                    task_vals['planned_hours'] = line.planned_hours
                elif 'allocated_hours' in available_task_fields:
                    task_vals['allocated_hours'] = line.planned_hours
                
                # Set task deadline based on delay
                if line.delay_days > 0:
                    task_vals['date_deadline'] = project_start + timedelta(days=line.delay_days)
                
                # Set assignee (check if field is user_ids or user_id)
                if 'user_ids' in available_task_fields:
                    if line.user_id:
                        task_vals['user_ids'] = [(6, 0, [line.user_id.id])]
                    elif self.user_id:
                        task_vals['user_ids'] = [(6, 0, [self.user_id.id])]
                elif 'user_id' in available_task_fields:
                    if line.user_id:
                        task_vals['user_id'] = line.user_id.id
                    elif self.user_id:
                        task_vals['user_id'] = self.user_id.id
                
                # Set stage if specified
                if line.stage_id:
                    task_vals['stage_id'] = line.stage_id.id
                
                self.env['project.task'].create(task_vals)
        
        return project
    
    def _trigger_state_activities(self, old_state, new_state):
        """Trigger automated activities when tender state changes"""
        self.ensure_one()
        
        activities_map = {
            'draft': self._activity_draft_qualification,
            'technical': self._activity_technical_study,
            'financial': self._activity_financial_study,
            'quotation': self._activity_quotation_review,
            'submitted': self._activity_post_submission,
            'evaluation': self._activity_under_evaluation,
        }
        
        activity_method = activities_map.get(new_state)
        if activity_method:
            activity_method()
    
    def _activity_draft_qualification(self):
        """Activities for Draft/Qualification phase"""
        self.ensure_one()
        
        # Activity 1: Download Etimad documents
        if self.etimad_tender_id or self.etimad_link:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('📥 Download Tender Documents from Etimad'),
                note=_(
                    '<strong>Action Required:</strong><br/>'
                    '<ul>'
                    '<li>Login to your Etimad account</li>'
                    '<li>Download all tender documents</li>'
                    '<li>Review technical specifications</li>'
                    '<li>Attach documents to this tender</li>'
                    '</ul>'
                    '<br/><strong>Etimad Link:</strong> %s'
                ) % (self.etimad_link or 'Check Etimad Portal'),
                user_id=self.user_id.id,
                date_deadline=fields.Date.today()
            )
        
        # Activity 2: Site visit scheduling (if required)
        if self.site_visit_required and not self.site_visit_date:
            self._schedule_site_visit_activity()
    
    def _schedule_site_visit_activity(self):
        """Schedule site visit activity"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_meeting',
            summary=_('📍 Schedule Site Visit (الزيارة الميدانية)'),
            note=_(
                '<strong>Site Visit Required</strong><br/>'
                '<ul>'
                '<li>Coordinate site visit date with customer</li>'
                '<li>Prepare required documents for site</li>'
                '<li>Assign team members for visit</li>'
                '<li>Update site visit date in tender form</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=self.last_inquiry_date or fields.Date.today()
        )
    
    def _activity_technical_study(self):
        """Activities for Technical Study phase"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('📋 Complete Technical Study & BoQ'),
            note=_(
                '<strong>Technical Phase Tasks:</strong><br/>'
                '<ul>'
                '<li>Review technical specifications</li>'
                '<li>Import/create Bill of Quantities</li>'
                '<li>Define product requirements</li>'
                '<li>Identify potential vendors</li>'
                '<li>Estimate quantities and costs</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=fields.Date.today()
        )
    
    def _activity_financial_study(self):
        """Activities for Financial Study phase"""
        self.ensure_one()
        
        # Activity: Request vendor quotes
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('💰 Request Vendor Quotations'),
            note=_(
                '<strong>Financial Phase Tasks:</strong><br/>'
                '<ul>'
                '<li>Send RFQs to selected vendors</li>'
                '<li>Collect and review vendor offers</li>'
                '<li>Compare vendor prices</li>'
                '<li>Select best vendors per product</li>'
                '<li>Calculate final margin</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=fields.Date.today()
        )
    
    def _activity_quotation_review(self):
        """Activities for Quotation phase"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('📄 Review & Approve Quotation'),
            note=_(
                '<strong>Quotation Review:</strong><br/>'
                '<ul>'
                '<li>Review generated quotation</li>'
                '<li>Verify prices and margins</li>'
                '<li>Get internal approvals</li>'
                '<li>Prepare submission documents</li>'
                '<li>Final quality check</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=self.submission_deadline.date() if self.submission_deadline else fields.Date.today()
        )
    
    def _activity_post_submission(self):
        """Activities after submission"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('✅ Confirm Submission & Track'),
            note=_(
                '<strong>Post-Submission:</strong><br/>'
                '<ul>'
                '<li>Confirm submission receipt from customer</li>'
                '<li>Monitor tender evaluation timeline</li>'
                '<li>Prepare for clarification questions</li>'
                '<li>Track opening date</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=self.opening_date.date() if self.opening_date else fields.Date.today()
        )
    
    def _activity_under_evaluation(self):
        """Activities during evaluation phase"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('🔍 Monitor Evaluation & Prepare Response'),
            note=_(
                '<strong>Evaluation Phase:</strong><br/>'
                '<ul>'
                '<li>Monitor customer evaluation progress</li>'
                '<li>Respond to clarification requests</li>'
                '<li>Prepare for negotiations if needed</li>'
                '<li>Track competitor information</li>'
                '<li>Stay ready for final presentations</li>'
                '</ul>'
            ),
            user_id=self.user_id.id,
            date_deadline=fields.Date.today()
        )
    
    def _trigger_appeal_option(self):
        """Trigger appeal workflow when tender is lost"""
        self.ensure_one()
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('⚖️ Consider Appeal (إعتراض) - You Have the Right!'),
            note=_(
                '<strong style="color: #d9534f;">Tender Lost - Appeal Option Available</strong><br/><br/>'
                
                '<strong>🔴 حق الإعتراض متاح:</strong><br/>'
                'الشركة لها الحق في تقديم إعتراض على نتيجة المنافسة.<br/><br/>'
                
                '<strong>الخطوات المطلوبة:</strong><br/>'
                '<ol>'
                '<li><strong>إعداد خطاب الإعتراض:</strong> قم بإعداد خطاب رسمي يوضح أسباب الإعتراض</li>'
                '<li><strong>إرسال الإعتراض:</strong> قدم الخطاب للجهة المعنية عبر القنوات الرسمية</li>'
                '<li><strong>إنتظار الرد:</strong> راقب استجابة الجهة الحكومية</li>'
                '<li><strong>المتابعة:</strong> هناك إمكانية أن يتم قبول الطلب</li>'
                '</ol><br/>'
                
                '<strong>Actions in Tender Form:</strong><br/>'
                '<ul>'
                '<li>Go to "Offer Results" tab</li>'
                '<li>Check "Appeal Submitted" checkbox</li>'
                '<li>Upload appeal letter</li>'
                '<li>Enter appeal reason</li>'
                '<li>Set submission date</li>'
                '<li>Track response status</li>'
                '</ul><br/>'
                
                '<strong>⏰ Act quickly - appeals are usually time-sensitive!</strong>'
            ),
            user_id=self.user_id.id,
            date_deadline=fields.Date.today()
        )

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
        if not self.partner_id:
            raise UserError(_('Please set a Customer before submitting the tender.'))
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
