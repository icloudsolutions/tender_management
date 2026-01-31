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
    tender_purpose = fields.Text("Tender Purpose", help="الغرض من المنافسة")
    
    # Hijri Dates (as text)
    last_enquiry_date_hijri = fields.Char("Last Enquiry Date (Hijri)")
    last_offer_date_hijri = fields.Char("Last Offer Date (Hijri)")
    
    # ICS Tender Integration
    tender_id_ics = fields.Many2one('ics.tender', string='ICS Tender', readonly=True,
        help='Direct link to ICS Tender (bypasses CRM)',
        ondelete='set null')  # Set to null if tender is deleted
    
    # ========== ENHANCED FIELDS FROM ETIMAD DETAIL PAGES ==========
    
    # Contract & Duration
    contract_duration = fields.Char("Contract Duration", help="مدة العقد (e.g., 10 يوم)")
    contract_duration_days = fields.Integer("Contract Duration (Days)", help="Contract duration in days")
    
    # Insurance & Guarantees
    insurance_required = fields.Boolean("Insurance Required", help="هل التأمين من متطلبات المنافسة")
    initial_guarantee_required = fields.Boolean("Initial Guarantee Required", help="مطلوب ضمان الإبتدائي")
    initial_guarantee_type = fields.Char("Initial Guarantee Type", help="نوع الضمان الإبتدائي (e.g., لا يوجد ضمان)")
    
    # Document Cost
    document_cost_type = fields.Selection([
        ('free', 'Free / مجانا'),
        ('paid', 'Paid / مدفوع'),
    ], string="Document Cost Type", help="قيمة وثائق المنافسة")
    document_cost_amount = fields.Monetary("Document Cost Amount", currency_field='currency_id',
        help="Amount if documents are paid")
    
    # Tender Status Details
    tender_status_text = fields.Char("Tender Status Text", help="حالة المنافسة (e.g., معتمدة)")
    tender_status_approved = fields.Boolean("Tender Approved", compute='_compute_tender_status_approved', store=True,
        help="Whether tender is approved (معتمدة)")
    
    # Submission Method
    submission_method = fields.Selection([
        ('single_file', 'Single File (Technical & Financial) / ملف واحد للعرض الفني والمالي معا'),
        ('separate_files', 'Separate Files / ملفات منفصلة'),
        ('electronic', 'Electronic / إلكتروني'),
        ('manual', 'Manual / يدوي'),
    ], string="Submission Method", help="طريقة تقديم العروض")
    
    # Additional Dates
    offer_opening_date = fields.Datetime("Offer Opening Date", help="تاريخ فتح العروض")
    offer_examination_date = fields.Datetime("Offer Examination Date", help="تاريخ فحص العروض")
    expected_award_date = fields.Date("Expected Award Date", help="التاريخ المتوقع للترسية")
    work_start_date = fields.Date("Work Start Date", help="تاريخ بدء الأعمال / الخدمات")
    inquiry_start_date = fields.Date("Inquiry Start Date", help="بداية إرسال الأسئلة و الاستفسارات")
    max_inquiry_response_days = fields.Integer("Max Inquiry Response Days", 
        help="اقصى مدة للاجابة على الاستفسارات (in days)")
    
    # Location Information
    opening_location = fields.Char("Opening Location", help="مكان فتح العرض")
    execution_location_type = fields.Selection([
        ('inside_kingdom', 'Inside Kingdom / داخل المملكة'),
        ('outside_kingdom', 'Outside Kingdom / خارج المملكة'),
        ('both', 'Both / داخل وخارج المملكة'),
    ], string="Execution Location Type", help="مكان التنفيذ")
    execution_regions = fields.Text("Execution Regions", help="مناطق التنفيذ (JSON or text)")
    execution_cities = fields.Text("Execution Cities", help="مدن التنفيذ (JSON or text)")
    
    # Classification & Activities
    classification_field = fields.Char("Classification Field", help="مجال التصنيف")
    classification_required = fields.Boolean("Classification Required", 
        help="Whether classification is required (غير مطلوب = False)")
    activity_details = fields.Text("Activity Details", help="نشاط المنافسة (detailed list)")
    
    # Work Types
    includes_supply_items = fields.Boolean("Includes Supply Items", 
        help="تشمل المنافسة على بنود توريد")
    construction_works = fields.Text("Construction Works", help="أعمال الإنشاء")
    maintenance_works = fields.Text("Maintenance & Operation Works", help="أعمال الصيانة والتشغيل")
    
    # Award Information
    award_announced = fields.Boolean("Award Announced", default=False, 
        help="Whether award results have been announced")
    award_announcement_date = fields.Date("Award Announcement Date", 
        help="Date when award was announced")
    awarded_company_name = fields.Char("Awarded Company Name", help="اسم الشركة المرسية")
    awarded_amount = fields.Monetary("Awarded Amount", currency_field='currency_id',
        help="المبلغ المرسى عليه")
    
    # Agency Code (for logo)
    agency_code = fields.Char("Agency Code", help="Agency code for logo loading")
    tender_type_id = fields.Integer("Tender Type ID", help="Tender type ID from Etimad")

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
    
    @api.depends('tender_status_text')
    def _compute_tender_status_approved(self):
        """Check if tender status indicates approval"""
        for record in self:
            if record.tender_status_text:
                status_lower = record.tender_status_text.lower()
                record.tender_status_approved = any(word in status_lower for word in [
                    'معتمدة', 'approved', 'موافقة', 'accepted'
                ])
            else:
                record.tender_status_approved = False

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
            'agency_code': raw_data.get('agencyCode'),
            'tender_type_id': raw_data.get('tenderTypeId'),
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
    
    def _parse_contract_duration(self, duration_text):
        """Parse contract duration text to extract days (e.g., '10 يوم' -> 10)"""
        if not duration_text:
            return False, 0
        
        import re
        # Try to extract number from text
        numbers = re.findall(r'\d+', duration_text)
        if numbers:
            days = int(numbers[0])
            return duration_text, days
        
        return duration_text, 0

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
    
    def action_fetch_detailed_info(self):
        """Fetch detailed tender information from Etimad detail page"""
        self.ensure_one()
        
        if not self.tender_id_string:
            raise UserError(_('Tender ID String is required to fetch detailed information.'))
        
        # Note: This would require API access or manual parsing
        # Since Etimad uses CAPTCHA, this is a placeholder for future enhancement
        # or manual data entry
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Fetch Detailed Info'),
                'message': _('Detailed information fetching requires API access or manual entry. Please use the Etimad portal to view full details.'),
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_open_detailed_report(self):
        """Open detailed tender report on Etimad portal"""
        self.ensure_one()
        if self.tender_id_string:
            return {
                'type': 'ir.actions.act_url',
                'url': f'https://tenders.etimad.sa/Tender/OpenTenderDetailsReportForVisitor?tenderIdString={self.tender_id_string}',
                'target': 'new'
            }
        raise UserError(_('Tender ID String is required.'))
    
    def action_open_details_page(self):
        """Open tender details page on Etimad portal"""
        self.ensure_one()
        if self.tender_id_string:
            return {
                'type': 'ir.actions.act_url',
                'url': f'https://tenders.etimad.sa/Tender/DetailsForVisitor?STenderId={self.tender_id_string}',
                'target': 'new'
            }
        raise UserError(_('Tender ID String is required.'))
    
    def read(self, fields=None, load='_classic_read'):
        """Override read to handle invalid tender_id_ics references gracefully"""
        # Check if we're already in cleanup mode to prevent infinite recursion
        if self.env.context.get('_cleaning_tender_refs'):
            # In cleanup mode, exclude tender_id_ics from read
            if fields is None:
                # Read all fields except tender_id_ics
                all_fields = list(self._fields.keys())
                safe_fields = [f for f in all_fields if f != 'tender_id_ics']
                result = super(EtimadTender, self).read(fields=safe_fields, load=load)
            elif 'tender_id_ics' in fields:
                safe_fields = [f for f in fields if f != 'tender_id_ics']
                result = super(EtimadTender, self).read(fields=safe_fields, load=load)
            else:
                result = super(EtimadTender, self).read(fields=fields, load=load)
            
            # Manually add tender_id_ics as False for each record
            for record_data in result:
                record_data['tender_id_ics'] = False
            return result
        
        try:
            return super(EtimadTender, self).read(fields=fields, load=load)
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