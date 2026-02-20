# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_create_smb_quotation(self):
        """Create a new quotation from this opportunity and open it (SMB flow)."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Please set a customer on the opportunity first.'))
        # sale_crm adds opportunity_id to sale.order; use it if available
        context = dict(self.env.context)
        context['default_partner_id'] = self.partner_id.id
        context['default_user_id'] = self.user_id.id if self.user_id else self.env.user.id
        context['default_team_id'] = self.team_id.id if self.team_id else False
        if hasattr(self.env['sale.order'], 'opportunity_id'):
            context['default_opportunity_id'] = self.id
        return {
            'name': _('New Quotation (SMB)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'context': context,
        }
