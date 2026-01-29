from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    tender_ids = fields.One2many('ics.tender', 'lead_id', string='Tenders')
    tender_count = fields.Integer('Tender Count', compute='_compute_tender_count')

    etimad_tender_id = fields.Many2one('etimad.tender', string='Etimad Tender')

    @api.depends('tender_ids')
    def _compute_tender_count(self):
        for lead in self:
            lead.tender_count = len(lead.tender_ids)

    def action_view_tenders(self):
        self.ensure_one()
        return {
            'name': 'Tenders',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender',
            'view_mode': 'tree,form,kanban',
            'domain': [('lead_id', '=', self.id)],
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
                'default_team_id': self.team_id.id,
            },
        }

    def action_create_tender(self):
        self.ensure_one()
        return {
            'name': 'Create Tender',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender',
            'view_mode': 'form',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
                'default_team_id': self.team_id.id,
                'default_expected_revenue': self.expected_revenue,
                'default_etimad_tender_id': self.etimad_tender_id.id if self.etimad_tender_id else False,
            },
            'target': 'current',
        }
