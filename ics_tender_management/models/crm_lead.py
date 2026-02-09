from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    tender_ids = fields.One2many('ics.tender', 'lead_id', string='Tenders')
    tender_count = fields.Integer('Tender Count', compute='_compute_tender_count')

    etimad_tender_id = fields.Many2one('ics.etimad.tender', string='Etimad Tender')
    
    # Control fields for Etimad-sourced opportunities
    is_from_etimad = fields.Boolean('Created from Etimad', 
        compute='_compute_is_from_etimad', store=True,
        help='This opportunity was created from Etimad tender and is controlled by Tender Management')
    
    active_tender_id = fields.Many2one('ics.tender', 
        string='Active Tender', compute='_compute_active_tender', store=True,
        help='The primary active tender linked to this opportunity')
    
    @api.depends('etimad_tender_id')
    def _compute_is_from_etimad(self):
        """Mark opportunities created from Etimad scraper"""
        for lead in self:
            lead.is_from_etimad = bool(lead.etimad_tender_id)
    
    @api.depends('tender_ids', 'tender_ids.state')
    def _compute_active_tender(self):
        """Find the most recent active tender"""
        for lead in self:
            if lead.tender_ids:
                # Get most recent non-cancelled tender
                active_tender = lead.tender_ids.filtered(
                    lambda t: t.state != 'cancelled'
                ).sorted('create_date', reverse=True)
                lead.active_tender_id = active_tender[0] if active_tender else False
            else:
                lead.active_tender_id = False

    @api.depends('tender_ids')
    def _compute_tender_count(self):
        for lead in self:
            lead.tender_count = len(lead.tender_ids)
    
    def write(self, vals):
        """Prevent editing Etimad-sourced opportunities from CRM"""
        # Check if trying to change critical fields from CRM interface
        protected_fields = {'stage_id', 'probability', 'expected_revenue', 'date_deadline'}
        
        if any(field in vals for field in protected_fields):
            for lead in self:
                # Allow if no active tender or if called from tender module
                if lead.active_tender_id and not self._context.get('from_tender_sync'):
                    raise UserError(_(
                        'This opportunity is controlled by Tender Management.\n\n'
                        'Linked Tender: %s\n'
                        'Current State: %s\n\n'
                        'To modify this opportunity, please update the tender instead.\n'
                        'Changes to the tender will automatically sync to this opportunity.'
                    ) % (lead.active_tender_id.name, 
                         dict(lead.active_tender_id._fields['state'].selection).get(lead.active_tender_id.state)))
        
        return super(CrmLead, self).write(vals)

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
                
                # Etimad Identifiers
                'etimad_tender_id_integer': etimad.tender_id,
                'etimad_tender_id_string': etimad.tender_id_string,
                'etimad_reference_number': etimad.reference_number,
                
                # Agency Information (from Etimad)
                'etimad_agency_name': etimad.agency_name,
                'etimad_branch_name': etimad.branch_name,
                
                # Tender Activity (from Etimad)
                'etimad_activity_name': etimad.activity_name,
                'etimad_activity_id': etimad.activity_id,
                
                # Dates from Etimad
                'announcement_date': etimad.published_at.date() if etimad.published_at else False,
                'etimad_published_at': etimad.published_at,
                'submission_deadline': etimad.offers_deadline or etimad.submission_date,
                'opening_date': etimad.submission_date,
                'last_inquiry_date': etimad.last_enquiry_date.date() if etimad.last_enquiry_date else False,
                
                # Financial from Etimad
                'tender_booklet_price': etimad.document_cost_amount or 0.0,
                'etimad_financial_fees': 0.0,
                'estimated_project_value': etimad.document_cost_amount or 0.0,
                
                # External Source
                'external_source': etimad.external_source or 'Etimad Portal',
                
                # Etimad Status
                'etimad_tender_status_id': etimad.tender_status_id,
                
                # Hijri Dates (as text from Etimad)
                'etimad_last_enquiry_date_hijri': etimad.last_enquiry_date_hijri,
                'etimad_last_offer_date_hijri': etimad.last_offer_date_hijri,
                
                # Favorite Flag
                'is_favorite': etimad.is_favorite,
                
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
        activity_text = etimad.activity_name or etimad.etimad_tender_type or ''
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
