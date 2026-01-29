from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Auto Sync Settings
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
        help="Number of tenders to fetch in each synchronization"
    )
    
    # Auto Create Opportunity Settings
    etimad_auto_create_opportunity = fields.Boolean(
        string="Auto Create Opportunities",
        config_parameter="ics_etimad_tenders_crm.etimad_auto_create_opportunity",
        default=False,
        help="Automatically create CRM opportunities for new tenders"
    )
    
    etimad_min_tender_value = fields.Float(
        string="Minimum Tender Value",
        config_parameter="ics_etimad_tenders_crm.etimad_min_tender_value",
        default=10000.0,
        help="Minimum tender value (SAR) to auto-create opportunity"
    )
    
    # Notification Settings
    etimad_notify_new_tenders = fields.Boolean(
        string="Notify on New Tenders",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_new_tenders",
        default=True,
        help="Send notification when new tenders are fetched"
    )
    
    etimad_notify_urgent_deadlines = fields.Boolean(
        string="Notify Urgent Deadlines",
        config_parameter="ics_etimad_tenders_crm.etimad_notify_urgent_deadlines",
        default=True,
        help="Send notification for tenders with deadline in 3 days or less"
    )
    
    # Archive Settings
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