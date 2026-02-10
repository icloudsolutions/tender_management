from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompanyEtimad(models.Model):
    """Extend res.company to store Etimad Many2many settings persistently.
    
    Many2many fields cannot use config_parameter on res.config.settings
    (transient model). We store them on res.company instead and use
    related fields on res.config.settings.
    """
    _inherit = 'res.company'

    etimad_preferred_activities_ids = fields.Many2many(
        'ics.etimad.activity',
        'etimad_company_activity_rel',
        'company_id',
        'activity_id',
        string="Preferred Activities",
        help="Company's main business activities from Etimad classification."
    )

    etimad_notification_user_ids = fields.Many2many(
        'res.users',
        'etimad_company_notification_users_rel',
        'company_id',
        'user_id',
        string="Notification Recipients",
        help="Users who will receive tender notifications."
    )


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
        help="How often to sync tenders (in hours). Minimum: 1 hour, Recommended: 24 hours"
    )
    
    etimad_fetch_page_size = fields.Integer(
        string="Tenders per Sync",
        config_parameter="ics_etimad_tenders_crm.etimad_fetch_page_size",
        default=50,
        help="Number of tenders to fetch in each synchronization (min: 10, max: 50)"
    )
    
    etimad_fetch_pages = fields.Integer(
        string="Pages per Sync",
        config_parameter="ics_etimad_tenders_crm.etimad_fetch_pages",
        default=1,
        help="Number of pages to fetch per sync (1 page = up to 50 tenders). Max recommended: 5"
    )
    
    etimad_max_retries = fields.Integer(
        string="Max Retries",
        config_parameter="ics_etimad_tenders_crm.etimad_max_retries",
        default=3,
        help="Number of retry attempts for failed scraping requests (min: 1, max: 10)"
    )
    
    # ==================== AUTO OPPORTUNITY CREATION ====================
    
    etimad_auto_create_opportunity = fields.Boolean(
        string="Auto Create Opportunities",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_create_opportunity",
        default=False,
        help="Automatically create CRM opportunities for new tenders"
    )
    
    etimad_min_tender_value = fields.Float(
        string="Minimum Tender Value (SAR)",
        config_parameter="ics_etimad_tenders_crm.etimad_min_tender_value",
        default=10000.0,
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
    
    # Many2many stored on res.company for persistence (transient model cannot persist M2M)
    etimad_preferred_activities_ids = fields.Many2many(
        related='company_id.etimad_preferred_activities_ids',
        readonly=False,
        string="Preferred Activities",
        help="Select your company's main business activities from Etimad classification. Tenders matching these activities will get higher scores."
    )
    
    # Deprecated - kept for backward compatibility, will be removed in future versions
    etimad_preferred_activities = fields.Char(
        string="Preferred Activities (Legacy)",
        config_parameter="ics_etimad_tenders_crm.etimad_preferred_activities",
        help="DEPRECATED: Use 'Preferred Activities' multi-select field above instead."
    )
    
    etimad_preferred_categories = fields.Char(
        string="Primary Business Categories",
        config_parameter="ics_etimad_tenders_crm.etimad_preferred_categories",
        help="Your company's business categories (comma-separated). Options: supply, services, construction, maintenance, consulting. Example: 'supply, maintenance'"
    )
    
    etimad_min_preparation_days = fields.Integer(
        string="Min Preparation Days",
        config_parameter="ics_etimad_tenders_crm.etimad_min_preparation_days",
        default=7,
        help="Minimum days needed to prepare a tender submission"
    )
    
    # Note: Target value range settings removed - estimated amounts not consistently published in Etimad
    
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
    
    # Many2many stored on res.company for persistence (transient model cannot persist M2M)
    etimad_notification_user_ids = fields.Many2many(
        related='company_id.etimad_notification_user_ids',
        readonly=False,
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
    
    def set_values(self):
        """Override to update cron interval when scraping settings change"""
        res = super(ResConfigSettings, self).set_values()
        
        # Update cron job interval when scraping settings are saved
        try:
            self.env['ics.etimad.tender'].sudo().update_cron_interval()
        except Exception:
            pass  # Silently fail if cron update fails
        
        return res
    
    @api.constrains('etimad_sync_interval')
    def _check_sync_interval(self):
        """Validate sync interval is within acceptable range"""
        for record in self:
            if record.etimad_sync_interval and record.etimad_sync_interval < 1:
                raise ValidationError("Sync interval must be at least 1 hour.")
            if record.etimad_sync_interval and record.etimad_sync_interval > 168:  # 1 week
                raise ValidationError("Sync interval cannot exceed 168 hours (1 week).")
    
    @api.constrains('etimad_fetch_page_size')
    def _check_page_size(self):
        """Validate page size is within Etimad API limits"""
        for record in self:
            if record.etimad_fetch_page_size and record.etimad_fetch_page_size < 10:
                raise ValidationError("Page size must be at least 10.")
            if record.etimad_fetch_page_size and record.etimad_fetch_page_size > 50:
                raise ValidationError("Page size cannot exceed 50 (Etimad API limit).")
    
    @api.constrains('etimad_fetch_pages')
    def _check_fetch_pages(self):
        """Validate number of pages is reasonable"""
        for record in self:
            if record.etimad_fetch_pages and record.etimad_fetch_pages < 1:
                raise ValidationError("Must fetch at least 1 page.")
            if record.etimad_fetch_pages and record.etimad_fetch_pages > 10:
                raise ValidationError("Fetching more than 10 pages per sync may cause performance issues. Maximum allowed: 10.")
    
    @api.constrains('etimad_max_retries')
    def _check_max_retries(self):
        """Validate retry count is reasonable"""
        for record in self:
            if record.etimad_max_retries and record.etimad_max_retries < 1:
                raise ValidationError("Must allow at least 1 retry attempt.")
            if record.etimad_max_retries and record.etimad_max_retries > 10:
                raise ValidationError("Too many retries may cause excessive delays. Maximum allowed: 10.")