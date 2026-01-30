# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TenderTeam(models.Model):
    _name = 'ics.tender.team'
    _description = 'Tender Communication Team'
    _order = 'sequence, id'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    employee_id = fields.Many2one('res.users', string='Team Member', required=True)
    role = fields.Selection([
        ('responsible', 'Tender Responsible Employee'),
        ('technical', 'Technical Specialist'),
        ('financial', 'Financial Analyst'),
        ('legal', 'Legal Advisor'),
        ('sales', 'Sales Representative'),
        ('other', 'Other')
    ], string='Role', required=True, default='other')
    
    contact_info = fields.Char('Contact Info', related='employee_id.partner_id.email', readonly=True)
    phone = fields.Char('Phone', related='employee_id.partner_id.phone', readonly=True)
    
    notes = fields.Text('Notes')
