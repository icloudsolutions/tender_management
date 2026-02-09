# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeclineTenderWizard(models.TransientModel):
    _name = 'ics.tender.decline.wizard'
    _description = 'Decline Tender - Not Participating'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)
    tender_name = fields.Char(related='tender_id.name', string='Tender Number', readonly=True)
    tender_title = fields.Char(related='tender_id.tender_title', string='Tender Title', readonly=True)
    tender_state = fields.Selection(related='tender_id.state', string='Current State', readonly=True)

    non_participation_reason = fields.Text(
        'Reason for Not Participating', required=True,
        help='Explain why the company decided not to participate in this tender')

    def action_confirm_decline(self):
        """Decline tender participation and cancel the tender"""
        self.ensure_one()

        if not self.non_participation_reason:
            raise UserError(_('Please provide a reason for not participating.'))

        # Update tender
        self.tender_id.write({
            'participation_decision': False,
            'non_participation_reason': self.non_participation_reason,
            'state': 'cancelled',
        })

        # Log the decision in chatter
        state_label = dict(self.tender_id._fields['state'].selection).get(
            self.tender_state, self.tender_state)
        self.tender_id.message_post(
            body=_(
                '<strong>Tender Declined - Not Participating</strong><br/>'
                '<ul>'
                '<li><strong>Decision made at stage:</strong> %s</li>'
                '<li><strong>Reason:</strong> %s</li>'
                '</ul>'
            ) % (state_label, self.non_participation_reason),
            subject=_('Tender Declined'),
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tender Declined'),
                'message': _('The tender has been marked as Not Participating and cancelled.'),
                'type': 'warning',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }
