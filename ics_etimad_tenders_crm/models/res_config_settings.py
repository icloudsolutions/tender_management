from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ==================== SCRAPING & SYNC SETTINGS ====================
    
    etimad_auto_sync = fields.Boolean(
        string="Enable Auto Sync",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_sync",
        default=True,
        help="Automatically fetch new tenders from Etimad platform daily"
    )
    
    etimad_sync_interval = fields.Integer(
        string="Sync Interval (hours)",
        config_parameter="ics_etimad_tenders_crm.etimad_sync_interval",
        default=24,
        help="How often to sync tenders (in hours)"
    )
    
    etimad_fetch_page_size = fields.Integer(
        string="Tenders per Sync",
        config_parameter="ics_etimad_tenders_crm.etimad_fetch_page_size",
        default=50,
        help="Number of tenders to fetch in each synchronization (max: 50)"
    )
    
    etimad_fetch_pages = fields.Integer(
        string="Pages per Sync",
        config_parameter="ics_etimad_tenders_crm.etimad_fetch_pages",
        default=1,
        help="Number of pages to fetch per sync (1 page = up to 50 tenders)"
    )
    
    etimad_max_retries = fields.Integer(
        string="Max Retries",
        config_parameter="ics_etimad_tenders_crm.etimad_max_retries",
        default=3,
        help="Number of retry attempts for failed scraping requests"
    )
    
    # ==================== AUTO OPPORTUNITY CREATION ====================
    
    etimad_auto_create_opportunity = fields.Boolean(
        string="Auto Create Opportunities",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_create_opportunity",
        default=False,
        help="Automatically create CRM opportunities for new tenders"
    )
    
    etimad_min_tender_value = fields.Monetary(
        string="Minimum Tender Value",
        config_parameter="ics_etimad_tenders_crm.etimad_min_tender_value",
        default=10000.0,
        currency_field='company_currency_id',
        help="Minimum tender value (SAR) to auto-create opportunity"
    )
    
    etimad_min_match_score = fields.Float(
        string="Minimum Match Score (%)",
        config_parameter="ics_etimad_tenders_crm.etimad_min_match_score",
        default=50.0,
        help="Only create opportunities for tenders with match score above this threshold"
    )
    
    etimad_auto_assign_salesperson = fields.Boolean(
        string="Auto Assign Salesperson",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_assign_salesperson",
        default=True,
        help="Automatically assign opportunities to salespeople based on tender category"
    )
    
    # ==================== SMART MATCHING SETTINGS ====================
    
    etimad_enable_matching = fields.Boolean(
        string="Enable Smart Matching",
        config_parameter="ics_etimad_tenders_crm.etimad_enable_matching",
        default=True,
        help="Calculate matching scores for tenders based on company profile"
    )
    
    etimad_preferred_agencies = fields.Char(
        string="Preferred Agencies",
        config_parameter="ics_etimad_tenders_crm.etimad_preferred_agencies",
        help="List of preferred agency names (comma-separated). Tenders from these agencies get higher match scores."
    )
    
    etimad_preferred_activities = fields.Char(
        string="Preferred Activities",
        config_parameter="ics_etimad_tenders_crm.etimad_preferred_activities",
        help="List of preferred tender activities (comma-separated). Matching activities get higher scores."
    )
    
    etimad_preferred_categories = fields.Selection([
        ('supply', 'Supply / توريد'),
        ('services', 'Services / خدمات'),
        ('construction', 'Construction / إنشاءات'),
        ('maintenance', 'Maintenance & Operation / صيانة وتشغيل'),
        ('consulting', 'Consulting / استشارات'),
    ], string="Primary Business Category",
       config_parameter="ics_etimad_tenders_crm.etimad_preferred_categories",
       help="Your company's primary business category for tender matching")
    
    etimad_min_value_target = fields.Monetary(
        string="Minimum Target Value",
        config_parameter="ics_etimad_tenders_crm.etimad_min_value_target",
        default=50000.0,
        currency_field='company_currency_id',
        help="Minimum tender value your company typically pursues"
    )
    
    etimad_max_value_target = fields.Monetary(
        string="Maximum Target Value",
        config_parameter="ics_etimad_tenders_crm.etimad_max_value_target",
        default=5000000.0,
        currency_field='company_currency_id',
        help="Maximum tender value your company can handle"
    )
    
    etimad_min_preparation_days = fields.Integer(
        string="Min Preparation Days",
        config_parameter="ics_etimad_tenders_crm.etimad_min_preparation_days",
        default=7,
        help="Minimum days needed to prepare a tender submission"
    )
    
    # ==================== NOTIFICATION SETTINGS ====================
    
    etimad_notify_new_tenders = fields.Boolean(
        string="Notify on New Tenders",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_new_tenders",
        default=True,
        help="Send notification when new tenders are fetched"
    )
    
    etimad_notify_high_match = fields.Boolean(
        string="Notify High Match Tenders",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_high_match",
        default=True,
        help="Send notification for tenders with match score ≥70%"
    )
    
    etimad_notify_hot_tenders = fields.Boolean(
        string="Notify Hot Tenders",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_hot_tenders",
        default=True,
        help="Send notification for high-value urgent tenders"
    )
    
    etimad_notify_urgent_deadlines = fields.Boolean(
        string="Notify Urgent Deadlines",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_urgent_deadlines",
        default=True,
        help="Send notification for tenders with deadline ≤3 days"
    )
    
    etimad_notification_user_ids = fields.Many2many(
        'res.users',
        'etimad_notification_users_rel',
        'setting_id',
        'user_id',
        string="Notification Recipients",
        help="Users who will receive tender notifications"
    )
    
    # ==================== AUTO FETCH DETAILS SETTINGS ====================
    
    etimad_auto_fetch_details = fields.Boolean(
        string="Auto Fetch Details",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_fetch_details",
        default=False,
        help="Automatically fetch detailed information for high-match tenders"
    )
    
    etimad_fetch_details_threshold = fields.Float(
        string="Fetch Details for Match Score ≥",
        config_parameter="ics_etimad_tenders_crm.etimad_fetch_details_threshold",
        default=70.0,
        help="Automatically fetch details for tenders with this match score or higher"
    )
    
    # ==================== ARCHIVE SETTINGS ====================
    
    etimad_auto_archive = fields.Boolean(
        string="Auto Archive Old Tenders",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_archive",
        default=False,
        help="Automatically archive tenders after specified days"
    )
    
    etimad_archive_days = fields.Integer(
        string="Archive After Days",
        config_parameter="ics_etimad_tenders_crm.etimad_archive_days",
        default=90,
        help="Archive tenders this many days after their deadline"
    )
    
    etimad_archive_lost_only = fields.Boolean(
        string="Archive Lost/Cancelled Only",
        config_parameter="ics_etimad_tenders_crm.etimad_archive_lost_only",
        default=True,
        help="Only archive tenders in lost or cancelled state"
    )
    
    # ==================== CURRENCY ====================
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Company Currency",
        readonly=True
    )
    
    # ==================== ACTIONS ====================
    
    def action_test_scraping(self):
        """Test scraping connection"""
        self.ensure_one()
        tender_model = self.env['ics.etimad.tender']
        try:
            result = tender_model.fetch_etimad_tenders(page_size=5, page_number=1)
            return result
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test Failed',
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_manual_sync(self):
        """Manually trigger tender sync"""
        self.ensure_one()
        tender_model = self.env['ics.etimad.tender']
        page_size = self.etimad_fetch_page_size or 50
        pages = self.etimad_fetch_pages or 1
        
        return tender_model.fetch_etimad_tenders(
            page_size=page_size,
            page_number=1,
            max_pages=pages
        )
    
    def action_recalculate_match_scores(self):
        """Recalculate match scores for all tenders"""
        self.ensure_one()
        tender_model = self.env['ics.etimad.tender']
        tenders = tender_model.search([])
        
        # Trigger recomputation
        tenders._compute_matching_score()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Match Scores Recalculated',
                'message': f'Updated match scores for {len(tenders)} tenders',
                'type': 'success',
                'sticky': False,
            }
        }