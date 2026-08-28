# Extension of ics.etimad.tender: add Tender link and "Create Tender" action.
# This lives in ics_tender_management to avoid circular dependency.

from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EtimadTender(models.Model):
    _inherit = 'ics.etimad.tender'

    tender_id_ics = fields.Many2one(
        'ics.tender',
        string='Tender',
        readonly=True,
        help='Linked Tender record',
        ondelete='set null',
    )

    def action_create_tender_direct(self):
        """Create Tender from Etimad data.
        Fetches detailed info from Etimad first to ensure all data is available."""
        self.ensure_one()
        if self.tender_id_ics:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Tender'),
                'res_model': 'ics.tender',
                'res_id': self.tender_id_ics.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Fetch detailed info from Etimad before creating tender
        if self.tender_id_string:
            try:
                self._fetch_detailed_info_silent()
            except Exception as e:
                raise UserError(
                    _('Failed to fetch tender details from Etimad. '
                      'Please try again or fetch details manually first.\n\nError: %s') % str(e)
                )

        tender_vals = self._prepare_tender_vals_from_etimad()
        tender = self.env['ics.tender'].create(tender_vals)
        self.tender_id_ics = tender.id
        self.message_post(
            body=Markup(_('Tender created: <a href="/web#id=%s&model=ics.tender">%s</a>')) % (tender.id, tender.name),
            subject=_('Tender Created'),
            body_is_html=True,
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
        category = self._map_tender_category(self.activity_name or self.etimad_tender_type)
        partner = self._find_or_create_partner(self.agency_name)
        vals = {
            'tender_title': self.name,
            'tender_number': self.reference_number or self.tender_number or self.tender_id_string,
            'tender_category': category,
            'tender_type': 'product_wise',
            'description': self.description or '',
            'etimad_tender_id': self.id,
            'etimad_link': self.tender_url,
            'etimad_tender_id_integer': self.tender_id,
            'etimad_tender_id_string': self.tender_id_string,
            'etimad_reference_number': self.reference_number,
            'etimad_agency_name': self.agency_name,
            'etimad_branch_name': self.branch_name,
            'etimad_activity_name': self.activity_name,
            'etimad_activity_id': self.activity_id,
            'partner_id': partner.id if partner else False,
            'user_id': self.env.user.id,
            'announcement_date': self.published_at.date() if self.published_at else False,
            'etimad_published_at': self.published_at,
            'submission_deadline': self.offers_deadline or self.submission_date,
            'opening_date': self.submission_date,
            'last_inquiry_date': self.last_enquiry_date.date() if self.last_enquiry_date else False,
            'expected_revenue': self.estimated_amount or 0.0,
            'tender_booklet_price': self.document_cost_amount or 0.0,
            'estimated_project_value': self.estimated_amount or 0.0,
            'external_source': self.external_source or 'Etimad Portal',
            'etimad_tender_status_id': self.tender_status_id,
            'etimad_last_enquiry_date_hijri': self.last_enquiry_date_hijri,
            'etimad_last_offer_date_hijri': self.last_offer_date_hijri,
            'is_favorite': self.is_favorite,
            'tender_submission_method': self._map_submission_method(),
            'priority': '3' if self.remaining_days < 7 else '1',
            'state': 'draft',
        }
        return vals

    def _map_tender_category(self, activity_text):
        """Map Etimad activity to tender category"""
        if not activity_text:
            return 'other'
        activity_lower = activity_text.lower()
        if any(w in activity_lower for w in ['توريد', 'supply', 'توريدات', 'شراء', 'purchase']):
            return 'supply'
        if any(w in activity_lower for w in ['خدمات', 'service', 'استشار', 'consult']):
            return 'services'
        if any(w in activity_lower for w in ['إنشاء', 'construction', 'بناء', 'مباني']):
            return 'construction'
        if any(w in activity_lower for w in ['صيانة', 'maintenance', 'تشغيل', 'operation']):
            return 'maintenance'
        if any(w in activity_lower for w in ['استشار', 'consulting', 'دراس', 'study']):
            return 'consulting'
        return 'other'

    def _map_submission_method(self):
        return 'electronic'

    def _find_or_create_partner(self, agency_name):
        if not agency_name:
            return False
        partner = self.env['res.partner'].search([('name', '=ilike', agency_name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': agency_name,
                'is_company': True,
                'customer_rank': 1,
                'comment': 'Created from Etimad tender scraper',
            })
        return partner
