# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    smb_require_credit_approval = fields.Boolean(
        string='Require Credit Approval Before Confirm',
        default=True,
        help='When enabled, Sale Orders must be Credit Approved (SMB workflow) before they can be confirmed.',
    )
    smb_default_project_template_id = fields.Many2one(
        'smb.project.task.template',
        string='Default Delivery Project Template',
        help='Default task template when creating a delivery project from a Sale Order.',
    )
