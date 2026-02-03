# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TenderSupplier(models.Model):
    _name = 'ics.tender.supplier'
    _description = 'Tender Potential Suppliers'
    _order = 'sequence, id'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True, 
        domain=['|', ('supplier_rank', '>', 0), ('is_company', '=', True)])
    
    # Supplier Scope
    scope_of_work = fields.Text('Scope of Work / Scope within Tender')
    
    # Evaluation Fields
    evaluation_score = fields.Float('Evaluation Score', help='Evaluation score from criteria')
    account_receivable = fields.Monetary('Account Receivable', currency_field='currency_id')
    account_payable = fields.Monetary('Account Payable', currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        related='tender_id.currency_id', readonly=True)
    
    # Contact Information
    phone = fields.Char('Phone', related='partner_id.phone', readonly=True)
    email = fields.Char('Email', related='partner_id.email', readonly=True)
    city = fields.Char('City', related='partner_id.city', readonly=True)
    country_id = fields.Many2one('res.country', string='Country', related='partner_id.country_id', readonly=True)
    
    # Status
    status = fields.Selection([
        ('potential', 'Potential'),
        ('invited', 'Invited'),
        ('responded', 'Responded'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected')
    ], string='Status', default='potential', required=True)
    
    notes = fields.Text('Notes')
