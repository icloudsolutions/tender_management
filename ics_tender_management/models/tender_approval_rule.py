# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TenderApprovalRule(models.Model):
    _name = 'ics.tender.approval.rule'
    _description = 'Tender Approval Rule Configuration'
    _order = 'sequence, amount_threshold desc'
    
    name = fields.Char('Rule Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10, 
        help='Lower sequence = higher priority')
    
    # Conditions
    tender_category = fields.Selection([
        ('supply', 'Supply (توريد)'),
        ('services', 'Services'),
        ('construction', 'Construction'),
        ('maintenance', 'Maintenance & Operation (صيانة و تشغيل)'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ], string='Tender Category', 
        help='Leave empty to apply to all categories')
    
    amount_threshold = fields.Monetary('Amount Threshold', 
        currency_field='currency_id',
        help='Minimum tender amount for this rule to apply. Leave 0 for all amounts.')
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)
    
    # Required Approvals
    require_direct_manager = fields.Boolean('Direct Manager Approval', default=False)
    require_department_manager = fields.Boolean('Department Manager Approval', default=False)
    require_financial_manager = fields.Boolean('Financial Manager Approval', default=False)
    require_ceo = fields.Boolean('CEO Approval', default=False)
    
    # Additional conditions
    apply_to_all_states = fields.Boolean('Apply to All States', default=False,
        help='If checked, rule applies regardless of tender state')
    
    applicable_states = fields.Selection([
        ('quotation', 'Quotation Prepared'),
        ('submitted', 'Submitted'),
        ('evaluation', 'Under Evaluation'),
    ], string='Applicable States', default='quotation',
        help='States where this approval rule applies')
    
    @api.constrains('amount_threshold')
    def _check_amount_threshold(self):
        for rule in self:
            if rule.amount_threshold < 0:
                raise ValidationError(_('Amount threshold cannot be negative.'))
    
    def _matches_tender(self, tender):
        """Check if this rule matches the given tender"""
        self.ensure_one()
        
        # Check category
        if self.tender_category and tender.tender_category != self.tender_category:
            return False
        
        # Check amount threshold
        if self.amount_threshold > 0:
            tender_amount = tender.total_quotation_amount or tender.expected_revenue or 0.0
            if tender_amount < self.amount_threshold:
                return False
        
        # Check state
        if not self.apply_to_all_states:
            if tender.state != self.applicable_states:
                return False
        
        return True
    
    @api.model
    def get_required_approvals_for_tender(self, tender):
        """Get required approvals for a tender based on matching rules"""
        rules = self.search([('active', '=', True)], order='sequence, amount_threshold desc')
        
        required_approvals = {
            'direct_manager': False,
            'department_manager': False,
            'financial_manager': False,
            'ceo': False,
        }
        
        # Find first matching rule (highest priority)
        for rule in rules:
            if rule._matches_tender(tender):
                required_approvals['direct_manager'] = rule.require_direct_manager
                required_approvals['department_manager'] = rule.require_department_manager
                required_approvals['financial_manager'] = rule.require_financial_manager
                required_approvals['ceo'] = rule.require_ceo
                break  # Use first matching rule
        
        return required_approvals
