# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EtimadConfigWizard(models.TransientModel):
    """Standalone Etimad configuration form.

    Replaces the res.config.settings app section to avoid the
    'Invalid fields: Document, Spreadsheet, Folder' error caused by the
    Documents Enterprise module on the main Settings page.
    All values are persisted to ir.config_parameter and res.company.
    """
    _name = 'ics.etimad.config.wizard'
    _description = 'Etimad Tenders Configuration'

    # ==================== SCRAPING & SYNC ====================
    etimad_auto_sync = fields.Boolean(string="Enable Auto Sync", default=True)
    etimad_sync_interval = fields.Integer(string="Sync Interval (hours)", default=24)
    etimad_fetch_page_size = fields.Integer(string="Tenders per Page", default=50)
    etimad_fetch_pages = fields.Integer(string="Pages per Sync", default=3)
    etimad_max_retries = fields.Integer(string="Max Retries", default=3)
    etimad_publish_date_filter = fields.Selection([
        ('0', 'All Tenders'),
        ('1', 'Today'),
        ('2', 'Yesterday'),
        ('3', 'Last Week'),
        ('4', 'Last Month'),
        ('5', 'Last 3 Months'),
    ], string="Publish Date Filter", default='0',
       help="Filter tenders by publish date on Etimad portal. 'All Tenders' fetches everything available.")

    # ==================== SMART MATCHING ====================
    etimad_enable_matching = fields.Boolean(string="Enable Smart Matching", default=True)
    etimad_preferred_activities_ids = fields.Many2many(
        'ics.etimad.activity',
        'ics_etimad_config_wizard_activity_rel',
        'wizard_id', 'activity_id',
        string="Preferred Activities",
    )
    etimad_preferred_categories = fields.Char(string="Primary Business Categories")
    etimad_preferred_agencies = fields.Char(string="Preferred Agencies")
    etimad_min_preparation_days = fields.Integer(string="Min Preparation Days", default=7)

    # ==================== AUTO OPPORTUNITY ====================
    etimad_auto_create_opportunity = fields.Boolean(string="Auto Create Opportunities", default=False)
    etimad_min_tender_value = fields.Float(string="Min Tender Value (SAR)", default=10000.0)
    etimad_min_match_score = fields.Float(string="Min Match Score (%)", default=50.0)
    etimad_auto_assign_salesperson = fields.Boolean(string="Auto Assign Salesperson", default=True)

    # ==================== AUTO FETCH DETAILS ====================
    etimad_auto_fetch_details = fields.Boolean(string="Auto Fetch Details", default=False)
    etimad_fetch_details_threshold = fields.Float(string="Fetch if Match Score ≥ (%)", default=70.0)

    # ==================== NOTIFICATIONS ====================
    etimad_notify_new_tenders = fields.Boolean(string="Notify on New Tenders", default=True)
    etimad_notify_high_match = fields.Boolean(string="Notify High Match (≥70%)", default=True)
    etimad_notify_hot_tenders = fields.Boolean(string="Notify Hot Tenders", default=True)
    etimad_notify_urgent_deadlines = fields.Boolean(string="Notify Urgent Deadlines (≤3 days)", default=True)
    etimad_notification_user_ids = fields.Many2many(
        'res.users',
        'ics_etimad_config_wizard_users_rel',
        'wizard_id', 'user_id',
        string="Notification Recipients",
    )

    # ==================== ARCHIVE ====================
    etimad_auto_archive = fields.Boolean(string="Auto Archive Old Tenders", default=False)
    etimad_archive_days = fields.Integer(string="Archive After Days", default=90)
    etimad_archive_lost_only = fields.Boolean(string="Archive Lost/Cancelled Only", default=True)

    # ==================== PARAM KEYS (helper) ====================
    _PARAM_FIELDS = {
        'etimad_auto_sync': ('ics_etimad_tenders_crm.etimad_auto_sync', 'bool', True),
        'etimad_sync_interval': ('ics_etimad_tenders_crm.etimad_sync_interval', 'int', 24),
        'etimad_fetch_page_size': ('ics_etimad_tenders_crm.etimad_fetch_page_size', 'int', 50),
        'etimad_fetch_pages': ('ics_etimad_tenders_crm.etimad_fetch_pages', 'int', 3),
        'etimad_max_retries': ('ics_etimad_tenders_crm.etimad_max_retries', 'int', 3),
        'etimad_publish_date_filter': ('ics_etimad_tenders_crm.etimad_publish_date_filter', 'str', '0'),
        'etimad_enable_matching': ('ics_etimad_tenders_crm.etimad_enable_matching', 'bool', True),
        'etimad_preferred_categories': ('ics_etimad_tenders_crm.etimad_preferred_categories', 'str', ''),
        'etimad_preferred_agencies': ('ics_etimad_tenders_crm.etimad_preferred_agencies', 'str', ''),
        'etimad_min_preparation_days': ('ics_etimad_tenders_crm.etimad_min_preparation_days', 'int', 7),
        'etimad_auto_create_opportunity': ('ics_etimad_tenders_crm.etimad_auto_create_opportunity', 'bool', False),
        'etimad_min_tender_value': ('ics_etimad_tenders_crm.etimad_min_tender_value', 'float', 10000.0),
        'etimad_min_match_score': ('ics_etimad_tenders_crm.etimad_min_match_score', 'float', 50.0),
        'etimad_auto_assign_salesperson': ('ics_etimad_tenders_crm.etimad_auto_assign_salesperson', 'bool', True),
        'etimad_auto_fetch_details': ('ics_etimad_tenders_crm.etimad_auto_fetch_details', 'bool', False),
        'etimad_fetch_details_threshold': ('ics_etimad_tenders_crm.etimad_fetch_details_threshold', 'float', 70.0),
        'etimad_notify_new_tenders': ('ics_etimad_tenders_crm.etimad_notify_new_tenders', 'bool', True),
        'etimad_notify_high_match': ('ics_etimad_tenders_crm.etimad_notify_high_match', 'bool', True),
        'etimad_notify_hot_tenders': ('ics_etimad_tenders_crm.etimad_notify_hot_tenders', 'bool', True),
        'etimad_notify_urgent_deadlines': ('ics_etimad_tenders_crm.etimad_notify_urgent_deadlines', 'bool', True),
        'etimad_auto_archive': ('ics_etimad_tenders_crm.etimad_auto_archive', 'bool', False),
        'etimad_archive_days': ('ics_etimad_tenders_crm.etimad_archive_days', 'int', 90),
        'etimad_archive_lost_only': ('ics_etimad_tenders_crm.etimad_archive_lost_only', 'bool', True),
    }

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        params = self.env['ir.config_parameter'].sudo()
        company = self.env.company

        for fname, (key, ftype, default) in self._PARAM_FIELDS.items():
            if fname not in fields_list:
                continue
            raw = params.get_param(key, str(default))
            if ftype == 'bool':
                res[fname] = raw == 'True'
            elif ftype == 'int':
                res[fname] = int(raw or default)
            elif ftype == 'float':
                res[fname] = float(raw or default)
            else:
                res[fname] = raw or ''

        if 'etimad_preferred_activities_ids' in fields_list:
            res['etimad_preferred_activities_ids'] = [(6, 0, company.etimad_preferred_activities_ids.ids)]
        if 'etimad_notification_user_ids' in fields_list:
            res['etimad_notification_user_ids'] = [(6, 0, company.etimad_notification_user_ids.ids)]
        return res

    def action_save(self):
        self.ensure_one()
        params = self.env['ir.config_parameter'].sudo()
        company = self.env.company

        for fname, (key, ftype, _default) in self._PARAM_FIELDS.items():
            val = getattr(self, fname)
            params.set_param(key, str(val if val is not False else ('' if ftype == 'str' else val)))

        company.sudo().write({
            'etimad_preferred_activities_ids': [(6, 0, self.etimad_preferred_activities_ids.ids)],
            'etimad_notification_user_ids': [(6, 0, self.etimad_notification_user_ids.ids)],
        })

        # Update cron interval
        try:
            self.env['ics.etimad.tender'].sudo().update_cron_interval()
        except Exception:
            pass

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Settings Saved',
                'message': 'Etimad Tenders configuration has been saved successfully.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_test_scraping(self):
        self.ensure_one()
        try:
            result = self.env['ics.etimad.tender'].fetch_etimad_tenders(page_size=5, page_number=1)
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
                },
            }

    def action_manual_sync(self):
        self.ensure_one()
        return self.env['ics.etimad.tender'].fetch_etimad_tenders(
            page_size=self.etimad_fetch_page_size or 50,
            page_number=1,
            max_pages=self.etimad_fetch_pages or 1,
        )

    def action_recalculate_match_scores(self):
        self.ensure_one()
        tenders = self.env['ics.etimad.tender'].search([])
        tenders._compute_matching_score()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Match Scores Recalculated',
                'message': f'Updated match scores for {len(tenders)} tenders',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_open_matching_rules(self):
        """Open Dynamic Matching Rules configuration."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Matching Rules',
            'res_model': 'ics.etimad.matching.rule',
            'view_mode': 'list,form',
            'context': {'default_active': True},
        }
