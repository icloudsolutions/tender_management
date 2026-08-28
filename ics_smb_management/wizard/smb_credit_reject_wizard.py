# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class SmbCreditRejectWizard(models.TransientModel):
    _name = 'smb.credit.reject.wizard'
    _description = 'SMB Credit Reject Reason'

    _DEFAULT_REASON = _(
        'Rejected by Credit Control. '
        'Please follow up with customer for payment clearance or credit limit increase.'
    )

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, readonly=True)
    reason_id = fields.Many2one(
        'smb.credit.reject.reason',
        string='Predefined Reason',
        help='Optional: select a reason from the list (manage via SMB → Configuration → Reject Reasons).',
    )
    reason_notes = fields.Text(
        string='Additional notes',
        help='Optional details or free-text reason if no predefined reason is selected.',
    )

    def action_reject(self):
        self.ensure_one()
        parts = []
        if self.reason_id:
            parts.append(self.reason_id.name)
        if self.reason_notes and self.reason_notes.strip():
            parts.append(self.reason_notes.strip())
        reason = '\n'.join(parts) if parts else self._DEFAULT_REASON
        self.order_id.action_smb_credit_reject(reason=reason)
        return {'type': 'ir.actions.act_window_close'}
