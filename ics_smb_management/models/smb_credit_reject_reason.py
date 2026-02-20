# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SmbCreditRejectReason(models.Model):
    _name = 'smb.credit.reject.reason'
    _description = 'SMB Credit Reject Reason'
    _order = 'sequence, id'

    name = fields.Char(string='Reason', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
