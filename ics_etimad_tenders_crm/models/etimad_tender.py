from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import time
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class EtimadTender(models.Model):
    _name = "ics.etimad.tender"
    _description = "Etimad Tender"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _order = "published_at desc"
    
    # Basic Information
    name = fields.Char("Tender Name", required=True, tracking=True)
    reference_number = fields.Char("Reference Number", index=True, tracking=True)
    tender_number = fields.Char("Tender Number", tracking=True)
    tender_id = fields.Integer("Tender ID")
    tender_id_string = fields.Char("Tender ID String")
    
    # Agency Information
    agency_name = fields.Char("Agency", tracking=True)
    branch_name = fields.Char("Branch")
    
    # Tender Details
    tender_type = fields.Char("Tender Type", tracking=True)
    activity_name = fields.Char("Tender Activity", tracking=True)
    activity_id = fields.Integer("Activity ID")
    
    # Dates
    created_on = fields.Datetime("Created on", default=fields.Datetime.now, readonly=True)
    published_at = fields.Datetime("Published At", tracking=True)
    submission_date = fields.Datetime("Submission Date")
    last_enquiry_date = fields.Datetime("Enquiries Deadline", tracking=True)
    offers_deadline = fields.Datetime("Offers Deadline", tracking=True)
    remaining_days = fields.Integer("Remaining Days", compute='_compute_remaining_days', store=True)
    
    # Financial
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                   default=lambda self: self.env.ref('base.SAR'))
    invitation_cost = fields.Monetary("Invitation Cost", currency_field='currency_id')
    financial_fees = fields.Monetary("Financial Fees", currency_field='currency_id')
    total_fees = fields.Monetary("Total Fees", compute='_compute_total_fees', 
                                  store=True, currency_field='currency_id')
    
    # URLs and External References
    tender_url = fields.Char("Etimad URL", compute='_compute_tender_url', store=True)
    external_source = fields.Char("External Source", default="Etimad Portal", readonly=True)
    
    # Status and Classification
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('qualification', 'Qualification'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='new', tracking=True)
    
    tender_status_id = fields.Integer("Tender Status ID")
    
    # CRM Integration
    opportunity_id = fields.Many2one('crm.lead', string="Opportunity", tracking=True)
    opportunity_count = fields.Integer("Opportunities", compute='_compute_opportunity_count')
    
    # Additional Info
    description = fields.Text("Description")
    notes = fields.Text("Internal Notes")
    is_favorite = fields.Boolean("Favorite", default=False)
    
    # Hijri Dates (as text)
    last_enquiry_date_hijri = fields.Char("Last Enquiry Date (Hijri)")
    last_offer_date_hijri = fields.Char("Last Offer Date (Hijri)")

    @api.depends('tender_id_string')
    def _compute_tender_url(self):
        """Generate Etimad tender URL"""
        for record in self:
            if record.tender_id_string:
                record.tender_url = f"https://tenders.etimad.sa/Tender/Details/{record.tender_id_string}"
            else:
                record.tender_url = False

    @api.depends('invitation_cost', 'financial_fees')
    def _compute_total_fees(self):
        """Calculate total fees"""
        for record in self:
            record.total_fees = record.invitation_cost + record.financial_fees

    @api.depends('offers_deadline')
    def _compute_remaining_days(self):
        """Calculate remaining days until deadline"""
        for record in self:
            if record.offers_deadline:
                delta = record.offers_deadline - fields.Datetime.now()
                record.remaining_days = max(0, delta.days)
            else:
                record.remaining_days = 0

    @api.depends('opportunity_id')
    def _compute_opportunity_count(self):
        """Count related opportunities"""
        for record in self:
            record.opportunity_count = 1 if record.opportunity_id else 0

    @api.model
    def _setup_scraper_session(self):
        """Setup session with proper headers to mimic browser"""
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://portal.etimad.sa/',
            'Origin': 'https://portal.etimad.sa',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        session.headers.update(headers)
        return session

    @api.model
    def fetch_etimad_tenders(self, page_size=20, page_number=1):
        """Fetch tenders from Etimad platform with retry mechanism"""
        session = self._setup_scraper_session()
        max_retries = 3
        
        # First, visit the main portal to get cookies
        try:
            session.get("https://portal.etimad.sa/", timeout=10)
            time.sleep(2)
        except Exception as e:
            _logger.warning(f"Could not access portal homepage: {e}")
        
        for attempt in range(max_retries):
            try:
                _logger.info(f"Attempt {attempt + 1} to fetch tenders...")
                
                timestamp = int(time.time() * 1000)
                url = "https://tenders.etimad.sa/Tender/AllSupplierTendersForVisitorAsync"
                
                params = {
                    'PublishDateId': 5,  # Recent tenders
                    'PageSize': page_size,
                    'PageNumber': page_number,
                    '_': timestamp
                }
                
                response = session.get(url, params=params, timeout=30)
                
                _logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200 and response.text.strip():
                    try:
                        data = response.json()
                        
                        if not data or 'data' not in data:
                            _logger.warning("No data in response")
                            time.sleep(3)
                            continue
                        
                        tenders = data.get('data', [])
                        _logger.info(f"Successfully fetched {len(tenders)} tenders")
                        
                        created_count = 0
                        updated_count = 0
                        
                        for tender_data in tenders:
                            is_new = self._process_tender_data(tender_data)
                            if is_new:
                                created_count += 1
                            else:
                                updated_count += 1
                        
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Tenders Synchronized'),
                                'message': _('%d tenders created, %d updated') % (created_count, updated_count),
                                'type': 'success',
                                'sticky': False,
                            }
                        }
                    
                    except json.JSONDecodeError as e:
                        _logger.error(f"JSON decode error: {e}")
                        if '<html' in response.text.lower():
                            raise UserError(_("Etimad portal is blocking requests. Please try again later."))
                
                time.sleep(3)
                
            except requests.RequestException as e:
                _logger.error(f"Request error (attempt {attempt + 1}): {e}")
                time.sleep(3)
        
        raise UserError(_("Failed to fetch tenders after %d attempts. The site may have anti-bot protection.") % max_retries)

    def _process_tender_data(self, raw_data):
        """Process and create/update tender record"""
        
        # Map the raw data to Odoo fields
        vals = {
            'name': raw_data.get('tenderName', 'Unnamed Tender'),
            'reference_number': raw_data.get('referenceNumber'),
            'tender_number': raw_data.get('tenderNumber'),
            'tender_id': raw_data.get('tenderId'),
            'tender_id_string': raw_data.get('tenderIdString'),
            'agency_name': raw_data.get('agencyName'),
            'branch_name': raw_data.get('branchName'),
            'tender_type': raw_data.get('tenderTypeName'),
            'activity_name': raw_data.get('tenderActivityName'),
            'activity_id': raw_data.get('tenderActivityId'),
            'last_enquiry_date': self._parse_date(raw_data.get('lastEnqueriesDate')),
            'offers_deadline': self._parse_date(raw_data.get('lastOfferPresentationDate')),
            'submission_date': self._parse_date(raw_data.get('submitionDate')),
            'invitation_cost': float(raw_data.get('invitationCost', 0) or 0),
            'financial_fees': float(raw_data.get('financialFees', 0) or 0),
            'tender_status_id': raw_data.get('tenderStatusId'),
            'last_enquiry_date_hijri': raw_data.get('lastEnqueriesDateHijri'),
            'last_offer_date_hijri': raw_data.get('lastOfferPresentationDateHijri'),
            'description': self._generate_description(raw_data),
        }
        
        # Map status
        status_map = {
            4: 'qualification',
            5: 'won',
            6: 'lost'
        }
        vals['state'] = status_map.get(raw_data.get('tenderStatusId'), 'new')
        
        # Check if tender already exists
        existing = self.search([
            '|',
            ('reference_number', '=', vals['reference_number']),
            ('tender_id', '=', vals['tender_id'])
        ], limit=1)
        
        if existing:
            existing.write(vals)
            _logger.info(f"Updated tender: {vals['name'][:50]}")
            return False
        else:
            self.create(vals)
            _logger.info(f"Created tender: {vals['name'][:50]}")
            return True

    def _parse_date(self, date_str):
        """Parse date string to datetime"""
        if not date_str:
            return False
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str.split('.')[0], fmt)
                except ValueError:
                    continue
        except Exception as e:
            _logger.warning(f"Could not parse date: {date_str}, error: {e}")
        
        return False

    def _generate_description(self, tender_data):
        """Generate detailed description from tender data"""
        desc = f"""
**Tender Details**
- Reference: {tender_data.get('referenceNumber', 'N/A')}
- Tender Number: {tender_data.get('tenderNumber', 'N/A')}
- Agency: {tender_data.get('agencyName', 'N/A')}
- Branch: {tender_data.get('branchName', 'N/A')}
- Activity: {tender_data.get('tenderActivityName', 'N/A')}
- Type: {tender_data.get('tenderTypeName', 'N/A')}

**Important Dates**
- Last Enquiry: {tender_data.get('lastEnqueriesDateHijri', 'N/A')} (Hijri)
- Last Offer: {tender_data.get('lastOfferPresentationDateHijri', 'N/A')} (Hijri)

**Financial Information**
- Invitation Cost: {tender_data.get('invitationCost', 0)} SAR
- Financial Fees: {tender_data.get('financialFees', 0)} SAR

**Time Remaining:** {tender_data.get('remainingDays', 0)} days
        """
        return desc.strip()

    def action_open_url(self):
        """Open tender URL in new window"""
        self.ensure_one()
        if self.tender_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.tender_url,
                'target': 'new'
            }

    def action_create_opportunity(self):
        """Create CRM opportunity from tender"""
        self.ensure_one()
        
        if self.opportunity_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Opportunity'),
                'res_model': 'crm.lead',
                'res_id': self.opportunity_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Create new opportunity
        opportunity_vals = {
            'name': self.name,
            'type': 'opportunity',
            'partner_name': self.agency_name,
            'description': self.description,
            'expected_revenue': self.total_fees,
            'date_deadline': self.offers_deadline,
            'priority': '2' if self.remaining_days < 7 else '1',
        }
        
        opportunity = self.env['crm.lead'].create(opportunity_vals)
        self.opportunity_id = opportunity.id
        
        # Log activity
        self.message_post(
            body=_('Opportunity created: <a href="/web#id=%s&model=crm.lead">%s</a>') % (opportunity.id, opportunity.name),
            subject=_('Opportunity Created')
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Opportunity'),
            'res_model': 'crm.lead',
            'res_id': opportunity.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_toggle_favorite(self):
        """Toggle favorite status"""
        for record in self:
            record.is_favorite = not record.is_favorite

    def action_view_opportunities(self):
        """View related opportunities"""
        self.ensure_one()
        if self.opportunity_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Opportunity'),
                'res_model': 'crm.lead',
                'res_id': self.opportunity_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    @api.model
    def action_fetch_tenders_cron(self):
        """Scheduled action to fetch tenders automatically"""
        try:
            _logger.info("Starting scheduled tender fetch...")
            self.fetch_etimad_tenders(page_size=50, page_number=1)
            _logger.info("Scheduled tender fetch completed successfully")
        except Exception as e:
            _logger.error(f"Scheduled tender fetch failed: {e}")

    def action_set_state(self, state):
        """Set tender state"""
        for record in self:
            record.state = state