# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EtimadTenderExtended(models.Model):
    _inherit = 'ics.etimad.tender'
    
    tender_id_ics = fields.Many2one('ics.tender', string='ICS Tender', readonly=True,
        help='Direct link to ICS Tender (bypasses CRM)',
        ondelete='set null')  # Set to null if tender is deleted
    
    def read(self, fields=None, load='_classic_read'):
        """Override read to handle invalid tender_id_ics references gracefully"""
        # Check if we're already in cleanup mode to prevent infinite recursion
        if self.env.context.get('_cleaning_tender_refs'):
            # In cleanup mode, exclude tender_id_ics from read
            if fields is None:
                # Read all fields except tender_id_ics
                all_fields = list(self._fields.keys())
                safe_fields = [f for f in all_fields if f != 'tender_id_ics']
                result = super(EtimadTenderExtended, self).read(fields=safe_fields, load=load)
            elif 'tender_id_ics' in fields:
                safe_fields = [f for f in fields if f != 'tender_id_ics']
                result = super(EtimadTenderExtended, self).read(fields=safe_fields, load=load)
            else:
                result = super(EtimadTenderExtended, self).read(fields=fields, load=load)
            
            # Manually add tender_id_ics as False for each record
            for record_data in result:
                record_data['tender_id_ics'] = False
            return result
        
        try:
            return super(EtimadTenderExtended, self).read(fields=fields, load=load)
        except (AttributeError, ValueError) as e:
            # Check if error is related to tender_id_ics field
            error_str = str(e).lower()
            if 'tender_id_ics' in error_str or '_unknown' in error_str or "'id'" in error_str:
                # Clean up invalid references first (only for this record)
                try:
                    # Check if ics_tender table exists
                    self.env.cr.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'ics_tender'
                        )
                    """)
                    table_exists = self.env.cr.fetchone()[0]
                    
                    record_ids = [r.id for r in self]
                    if record_ids:
                        if table_exists:
                            # Use SQL to directly fix these records
                            self.env.cr.execute("""
                                UPDATE ics_etimad_tender 
                                SET tender_id_ics = NULL 
                                WHERE id = ANY(%s)
                                AND tender_id_ics IS NOT NULL
                                AND NOT EXISTS (
                                    SELECT 1 FROM ics_tender WHERE id = ics_etimad_tender.tender_id_ics
                                )
                            """, (record_ids,))
                        else:
                            # Table doesn't exist, just set all to NULL
                            self.env.cr.execute("""
                                UPDATE ics_etimad_tender 
                                SET tender_id_ics = NULL 
                                WHERE id = ANY(%s)
                                AND tender_id_ics IS NOT NULL
                            """, (record_ids,))
                        self.env.cr.commit()
                except Exception as cleanup_error:
                    _logger.warning("Error cleaning up tender reference during read: %s", cleanup_error)
                    pass
                
                # Retry reading with cleanup context (will exclude tender_id_ics if needed)
                return self.with_context(_cleaning_tender_refs=True).read(fields=fields, load=load)
            else:
                # Different error, re-raise
                raise
    
    @api.model
    def _cleanup_invalid_tender_references(self):
        """Clean up invalid tender_id_ics references (for migration)"""
        if 'ics.tender' not in self.env:
            # Use SQL to clean up invalid references
            try:
                self.env.cr.execute("""
                    UPDATE ics_etimad_tender e
                    SET tender_id_ics = NULL
                    WHERE e.tender_id_ics IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM ics_tender t 
                        WHERE t.id = e.tender_id_ics
                    )
                """)
                self.env.cr.commit()
                return self.env.cr.rowcount
            except Exception:
                return 0
        
        # Use ORM to clean up
        try:
            # Get all records with tender_id_ics set
            self.env.cr.execute("""
                SELECT id, tender_id_ics 
                FROM ics_etimad_tender 
                WHERE tender_id_ics IS NOT NULL
            """)
            records_data = self.env.cr.fetchall()
            
            cleaned = 0
            tender_model = self.env['ics.tender']
            
            for record_id, tender_id in records_data:
                try:
                    # Check if tender exists
                    if not tender_model.browse(tender_id).exists():
                        # Tender doesn't exist, set to NULL
                        self.env.cr.execute(
                            "UPDATE ics_etimad_tender SET tender_id_ics = NULL WHERE id = %s",
                            (record_id,)
                        )
                        cleaned += 1
                except Exception:
                    # If check fails, assume invalid and set to NULL
                    self.env.cr.execute(
                        "UPDATE ics_etimad_tender SET tender_id_ics = NULL WHERE id = %s",
                        (record_id,)
                    )
                    cleaned += 1
            
            if cleaned > 0:
                self.env.cr.commit()
            
            return cleaned
        except Exception as e:
            _logger.warning("Error cleaning up invalid tender references: %s", e)
            return 0
    
    def action_create_tender_direct(self):
        """Create ICS Tender directly from Etimad (skip CRM)"""
        self.ensure_one()
        
        # Check if ics.tender model exists
        if 'ics.tender' not in self.env:
            raise UserError(_('ICS Tender Management module is not installed. Please install it first.'))
        
        if self.tender_id_ics:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Tender'),
                'res_model': 'ics.tender',
                'res_id': self.tender_id_ics.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Check if ics.tender model exists
        if 'ics.tender' not in self.env:
            raise UserError(_('ICS Tender Management module is not installed. Please install it first.'))
        
        # Map Etimad fields to ICS Tender
        tender_vals = self._prepare_tender_vals_from_etimad()
        
        tender = self.env['ics.tender'].create(tender_vals)
        self.tender_id_ics = tender.id
        
        # Log activity
        self.message_post(
            body=_('ICS Tender created directly: <a href="/web#id=%s&model=ics.tender">%s</a>') % (tender.id, tender.name),
            subject=_('Tender Created')
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender'),
            'res_model': 'ics.tender',
            'res_id': tender.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _prepare_tender_vals_from_etimad(self):
        """Prepare complete tender values from Etimad data"""
        self.ensure_one()
        
        # Determine tender category from activity
        category = self._map_tender_category(self.activity_name or self.tender_type)
        
        # Create/find partner for agency
        partner = self._find_or_create_partner(self.agency_name)
        
        vals = {
            # Basic Information
            'tender_title': self.name,
            'tender_number': self.reference_number or self.tender_number or self.tender_id_string,
            'tender_category': category,
            'tender_type': 'single_vendor',  # Default, user can change
            'description': self.description or '',
            
            # Etimad Link
            'etimad_tender_id': self.id,
            'etimad_link': self.tender_url,
            
            # Etimad Identifiers
            'etimad_tender_id_integer': self.tender_id,
            'etimad_tender_id_string': self.tender_id_string,
            'etimad_reference_number': self.reference_number,
            
            # Agency Information (from Etimad)
            'etimad_agency_name': self.agency_name,
            'etimad_branch_name': self.branch_name,
            
            # Tender Activity (from Etimad)
            'etimad_activity_name': self.activity_name,
            'etimad_activity_id': self.activity_id,
            
            # Partner & Team
            'partner_id': partner.id if partner else False,
            'user_id': self.env.user.id,
            
            # Dates
            'announcement_date': self.published_at.date() if self.published_at else False,
            'etimad_published_at': self.published_at,
            'submission_deadline': self.offers_deadline or self.submission_date,
            'opening_date': self.submission_date,
            'last_inquiry_date': self.last_enquiry_date.date() if self.last_enquiry_date else False,
            
            # Financial
            'expected_revenue': self.total_fees or 0.0,
            'tender_booklet_price': self.invitation_cost or 0.0,
            'etimad_financial_fees': self.financial_fees or 0.0,
            'estimated_project_value': self.total_fees or 0.0,
            
            # External Source
            'external_source': self.external_source or 'Etimad Portal',
            
            # Etimad Status
            'etimad_tender_status_id': self.tender_status_id,
            
            # Hijri Dates (as text from Etimad)
            'etimad_last_enquiry_date_hijri': self.last_enquiry_date_hijri,
            'etimad_last_offer_date_hijri': self.last_offer_date_hijri,
            
            # Favorite Flag
            'is_favorite': self.is_favorite,
            
            # Tender Details (Legacy CRM fields)
            'tender_submission_method': self._map_submission_method(),
            
            # Priority
            'priority': '3' if self.remaining_days < 7 else '1',
            
            # State
            'state': 'draft',
        }
        
        return vals
    
    def _map_tender_category(self, activity_text):
        """Map Etimad activity to tender category"""
        if not activity_text:
            return 'other'
        
        activity_lower = activity_text.lower()
        
        # Supply-related keywords
        if any(word in activity_lower for word in ['توريد', 'supply', 'توريدات', 'شراء', 'purchase']):
            return 'supply'
        
        # Services-related keywords
        elif any(word in activity_lower for word in ['خدمات', 'service', 'استشار', 'consult']):
            return 'services'
        
        # Construction-related keywords
        elif any(word in activity_lower for word in ['إنشاء', 'construction', 'بناء', 'مباني']):
            return 'construction'
        
        # Maintenance-related keywords
        elif any(word in activity_lower for word in ['صيانة', 'maintenance', 'تشغيل', 'operation']):
            return 'maintenance'
        
        # Consulting-related keywords
        elif any(word in activity_lower for word in ['استشار', 'consulting', 'دراس', 'study']):
            return 'consulting'
        
        else:
            return 'other'
    
    def _map_submission_method(self):
        """Determine submission method from Etimad data"""
        # Most Etimad tenders are electronic
        return 'electronic'
    
    def _find_or_create_partner(self, agency_name):
        """Find or create partner for government agency"""
        if not agency_name:
            return False
        
        # Search for existing partner
        partner = self.env['res.partner'].search([
            ('name', '=ilike', agency_name)
        ], limit=1)
        
        if not partner:
            # Create new partner for agency
            partner = self.env['res.partner'].create({
                'name': agency_name,
                'is_company': True,
                'customer_rank': 1,
                'comment': 'Created from Etimad tender scraper',
            })
        
        return partner
