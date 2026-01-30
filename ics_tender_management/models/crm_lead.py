from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    tender_ids = fields.One2many('ics.tender', 'lead_id', string='Tenders')
    tender_count = fields.Integer('Tender Count', compute='_compute_tender_count')

    etimad_tender_id = fields.Many2one('ics.etimad.tender', string='Etimad Tender')

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
            'view_mode': 'list,form,kanban',
            'domain': [('lead_id', '=', self.id)],
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
                'default_team_id': self.team_id.id,
            },
        }

    def action_create_tender(self):
        """Create tender from CRM opportunity with FULL data preservation"""
        self.ensure_one()
        
        # Prepare complete tender values
        tender_vals = self._prepare_tender_vals_from_lead()
        
        # Create tender
        tender = self.env['ics.tender'].create(tender_vals)
        
        # Log in CRM
        self.message_post(
            body=_('Tender created: <a href="/web#id=%s&model=ics.tender">%s</a>') % (tender.id, tender.name),
            subject=_('Tender Created')
        )
        
        return {
            'name': 'Tender',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender',
            'view_mode': 'form',
            'res_id': tender.id,
            'target': 'current',
        }
    
    def _prepare_tender_vals_from_lead(self):
        """Prepare comprehensive tender values preserving ALL Etimad data"""
        self.ensure_one()
        
        vals = {
            # Link to CRM
            'lead_id': self.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.user_id.id if self.user_id else self.env.user.id,
            'team_id': self.team_id.id if self.team_id else False,
            
            # Basic Info from CRM
            'tender_title': self.name,
            'description': self.description or '',
            'expected_revenue': self.expected_revenue,
            'priority': self.priority,
            'tag_ids': [(6, 0, self.tag_ids.ids)] if self.tag_ids else False,
            
            # Etimad Link
            'etimad_tender_id': self.etimad_tender_id.id if self.etimad_tender_id else False,
        }
        
        # If linked to Etimad tender, pull ALL data from there
        if self.etimad_tender_id:
            etimad = self.etimad_tender_id
            
            # Override with Etimad data (more complete)
            vals.update({
                'tender_number': etimad.reference_number or etimad.tender_number or etimad.tender_id_string,
                'tender_category': self._map_tender_category_from_etimad(etimad),
                'etimad_link': etimad.tender_url,
                
                # Dates from Etimad
                'announcement_date': etimad.published_at.date() if etimad.published_at else False,
                'submission_deadline': etimad.offers_deadline or etimad.submission_date,
                'opening_date': etimad.submission_date,
                'last_inquiry_date': etimad.last_enquiry_date.date() if etimad.last_enquiry_date else False,
                
                # Financial from Etimad
                'tender_booklet_price': etimad.invitation_cost or 0.0,
                'estimated_project_value': etimad.total_fees or 0.0,
                
                # Submission method
                'tender_submission_method': 'electronic',  # Etimad is electronic
            })
        else:
            # No Etimad link, use CRM data
            vals.update({
                'tender_number': self.name,  # Use opportunity name as fallback
                'tender_category': 'other',  # User must specify
                'submission_deadline': self.date_deadline if self.date_deadline else fields.Datetime.now(),
            })
        
        return vals
    
    def _map_tender_category_from_etimad(self, etimad):
        """Map Etimad activity to tender category"""
        activity_text = etimad.activity_name or etimad.tender_type or ''
        activity_lower = activity_text.lower()
        
        if any(word in activity_lower for word in ['توريد', 'supply', 'توريدات', 'شراء']):
            return 'supply'
        elif any(word in activity_lower for word in ['خدمات', 'service', 'استشار', 'consult']):
            return 'services'
        elif any(word in activity_lower for word in ['إنشاء', 'construction', 'بناء']):
            return 'construction'
        elif any(word in activity_lower for word in ['صيانة', 'maintenance', 'تشغيل']):
            return 'maintenance'
        elif any(word in activity_lower for word in ['استشار', 'consulting', 'دراس']):
            return 'consulting'
        else:
            return 'other'
