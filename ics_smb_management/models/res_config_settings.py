# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smb_require_credit_approval = fields.Boolean(
        related='company_id.smb_require_credit_approval',
        string='Require Credit Approval Before Confirm',
        readonly=False,
    )
    smb_default_project_template_id = fields.Many2one(
        related='company_id.smb_default_project_template_id',
        string='Default Delivery Project Template',
        readonly=False,
    )
