# -*- coding: utf-8 -*-
from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeclineTenderWizard(models.TransientModel):
    _name = 'ics.tender.decline.wizard'
    _description = 'Decline Tender - Not Participating'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)
    tender_name = fields.Char(related='tender_id.name', string='Tender Number', readonly=True)
    tender_title = fields.Char(related='tender_id.tender_title', string='Tender Title', readonly=True)
    tender_state = fields.Selection(related='tender_id.state', string='Current State', readonly=True)

    decline_reason_id = fields.Many2one(
        'ics.tender.decline.reason', string='Decline Reason',
        help='Select the reason for not participating')
    non_participation_reason = fields.Text(
        'Additional Notes',
        help='Optional additional details about the decline decision')

    def action_confirm_decline(self):
        """Decline tender participation and cancel the tender"""
        self.ensure_one()

        if not self.decline_reason_id:
            raise UserError(_('Please select a decline reason.'))

        # Update tender
        self.tender_id.write({
            'participation_decision': False,
            'decline_reason_id': self.decline_reason_id.id,
            'non_participation_reason': self.non_participation_reason or '',
            'state': 'cancelled',
        })

        # Log the decision in chatter
        state_label = dict(self.tender_id._fields['state'].selection).get(
            self.tender_state, self.tender_state)
        body = Markup(
            '<strong>Tender Declined - Not Participating</strong><br/>'
            '<ul>'
            '<li><strong>Decision made at stage:</strong> %s</li>'
            '<li><strong>Reason:</strong> %s</li>'
        ) % (state_label, self.decline_reason_id.name)
        if self.non_participation_reason:
            body += Markup('<li><strong>Notes:</strong> %s</li>') % self.non_participation_reason
        body += Markup('</ul>')

        self.tender_id.message_post(
            body=body,
            subject=_('Tender Declined'),
            body_is_html=True,
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
