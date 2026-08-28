from odoo import models, fields


class ResCompanyEtimad(models.Model):
    """Extend res.company to store Etimad Many2many settings persistently.

    Many2many fields cannot be stored on transient models (res.config.settings).
    We keep them on res.company so they survive transient record cleanup.
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


# Note: All Etimad settings UI has been moved to ics.etimad.config.wizard
# (Etimad Tenders → Configuration → Settings) to avoid the
# 'Invalid fields: Document, Spreadsheet, Folder' error caused by the
# Documents Enterprise module on the main Odoo Settings page.
# The ir.config_parameter keys remain the same for backward compatibility.
