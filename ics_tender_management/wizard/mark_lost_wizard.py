# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MarkLostWizard(models.TransientModel):
    _name = 'ics.tender.mark.lost.wizard'
    _description = 'Mark Tender as Lost Wizard'
    
    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)
    tender_name = fields.Char(related='tender_id.name', string='Tender Number', readonly=True)
    tender_title = fields.Char(related='tender_id.tender_title', string='Tender Title', readonly=True)
    
    lost_reason = fields.Text('Lost Reason', required=True, 
        help='Please explain why the tender was lost')
    
    # Optional: Also allow marking appeal info immediately
    immediate_appeal = fields.Boolean('Plan to Submit Appeal', 
        help='Check if you plan to submit an appeal (إعتراض)')
    
    appeal_notes = fields.Text('Initial Appeal Notes', 
        help='Any initial notes about the planned appeal')
    
    def action_confirm_lost(self):
        """Mark tender as lost with the provided reason"""
        self.ensure_one()
        
        if not self.lost_reason:
            raise UserError(_('Please provide a reason for losing the tender.'))
        
        # Prepare values
        vals = {
            'state': 'lost',
            'lost_reason': self.lost_reason,
        }
        
        # If planning appeal, set initial flag
        if self.immediate_appeal:
            vals['appeal_submitted'] = False  # Not yet submitted, just planning
            if self.appeal_notes:
                vals['notes'] = (self.tender_id.notes or '') + '\n\n--- Appeal Planning Notes ---\n' + self.appeal_notes
        
        # Update tender
        self.tender_id.write(vals)
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tender Marked as Lost'),
                'message': _('The tender has been marked as lost. An activity has been created to consider the appeal option.'),
                'type': 'warning',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }
