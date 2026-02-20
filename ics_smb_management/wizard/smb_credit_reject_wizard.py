# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class SmbCreditRejectWizard(models.TransientModel):
    _name = 'smb.credit.reject.wizard'
    _description = 'SMB Credit Reject Reason'

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, readonly=True)
    reason = fields.Text(
        string='Reject Reason',
        required=True,
        default=lambda self: _(
            'Rejected by Credit Control. '
            'Please follow up with customer for payment clearance or credit limit increase.'
        ),
        help='Reason for rejection (e.g. overdue payments, credit limit exceeded). '
             'Sales person will use this to inform the customer.',
    )

    def action_reject(self):
        self.ensure_one()
        self.order_id.action_smb_credit_reject(reason=self.reason)
        return {'type': 'ir.actions.act_window_close'}
