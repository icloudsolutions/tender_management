from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import time
import logging
import re
import html as html_module
from datetime import datetime

try:
    from lxml import html
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    _logger.warning("lxml not available, HTML parsing will be limited")

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
    estimated_amount = fields.Monetary("Estimated Amount", currency_field='currency_id',
                                        help="Estimated value of the tender contract")
    
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

    # ========== COMPUTED FIELDS ==========
    
    is_urgent = fields.Boolean("Urgent", compute='_compute_is_urgent', store=True,
                                help="Auto-set when remaining days < 3")
    is_hot_tender = fields.Boolean("Hot Tender", compute='_compute_is_hot_tender', store=True,
                                    help="High-value tender with approaching deadline")
    estimated_value_category = fields.Selection([
        ('small', 'Small (< 100K SAR)'),
        ('medium', 'Medium (100K-1M SAR)'),
        ('large', 'Large (1M-10M SAR)'),
        ('mega', 'Mega (> 10M SAR)'),
    ], string="Value Category", compute='_compute_estimated_value_category', store=True)
    
    # Scraping metadata
    last_scraped_at = fields.Datetime("Last Scraped At", readonly=True)
    scraping_error_count = fields.Integer("Scraping Errors", default=0, readonly=True)
    last_scraping_error = fields.Text("Last Scraping Error", readonly=True)
    scraping_status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], string="Scraping Status", default='pending', readonly=True)
    
    # Matching and scoring
    matching_score = fields.Float("Matching Score", 
                                   help="Auto-calculated based on company profile (0-100)",
                                   compute='_compute_matching_score', store=True)
    matching_reasons = fields.Text("Matching Reasons", compute='_compute_matching_score', store=True)
    
    @api.depends('remaining_days')
    def _compute_is_urgent(self):
        """Mark tender as urgent if deadline is very close"""
        for record in self:
            record.is_urgent = record.remaining_days > 0 and record.remaining_days <= 3
    
    @api.depends('estimated_amount', 'remaining_days')
    def _compute_is_hot_tender(self):
        """Identify high-value tenders with approaching deadline"""
        for record in self:
            is_high_value = record.estimated_amount and record.estimated_amount >= 500000
            is_deadline_soon = record.remaining_days > 0 and record.remaining_days <= 7
            record.is_hot_tender = is_high_value and is_deadline_soon
    
    @api.depends('estimated_amount')
    def _compute_estimated_value_category(self):
        """Categorize tender by estimated value"""
        for record in self:
            if not record.estimated_amount or record.estimated_amount == 0:
                record.estimated_value_category = False
            elif record.estimated_amount < 100000:
                record.estimated_value_category = 'small'
            elif record.estimated_amount < 1000000:
                record.estimated_value_category = 'medium'
            elif record.estimated_amount < 10000000:
                record.estimated_value_category = 'large'
            else:
                record.estimated_value_category = 'mega'
    
    @api.depends('activity_name', 'tender_type', 'agency_name', 'estimated_amount')
    def _compute_matching_score(self):
        """Calculate matching score based on company profile and preferences from settings"""
        for record in self:
            score = 0
            reasons = []
            
            # Get settings
            params = self.env['ir.config_parameter'].sudo()
            matching_enabled = params.get_param('ics_etimad_tenders_crm.etimad_enable_matching', 'True') == 'True'
            
            if not matching_enabled:
                record.matching_score = 0
                record.matching_reasons = False
                continue
            
            # Get configuration parameters
            preferred_agencies = params.get_param('ics_etimad_tenders_crm.etimad_preferred_agencies', '')
            preferred_activities = params.get_param('ics_etimad_tenders_crm.etimad_preferred_activities', '')
            preferred_categories_str = params.get_param('ics_etimad_tenders_crm.etimad_preferred_categories', '')
            min_value = float(params.get_param('ics_etimad_tenders_crm.etimad_min_value_target', '50000') or 0)
            max_value = float(params.get_param('ics_etimad_tenders_crm.etimad_max_value_target', '5000000') or 0)
            min_prep_days = int(params.get_param('ics_etimad_tenders_crm.etimad_min_preparation_days', '7') or 7)
            
            # Parse comma-separated lists
            agencies_list = [a.strip().lower() for a in preferred_agencies.split(',') if a.strip()] if preferred_agencies else []
            activities_list = [a.strip().lower() for a in preferred_activities.split(',') if a.strip()] if preferred_activities else []
            categories_list = [c.strip().lower() for c in preferred_categories_str.split(',') if c.strip()] if preferred_categories_str else []
            
            # Activity matching (30 points)
            if record.activity_name and activities_list:
                activity_lower = record.activity_name.lower()
                # Check for exact or partial match
                if activity_lower in activities_list:
                    score += 30
                    reasons.append(f'Activity "{record.activity_name}" matches preferences')
                elif any(pref in activity_lower or activity_lower in pref for pref in activities_list):
                    score += 20
                    reasons.append(f'Activity "{record.activity_name}" partially matches preferences')
            
            # Tender type / Category matching (20 points)
            # Check if tender matches any of the preferred categories
            if categories_list:
                type_lower = (record.tender_type or '').lower()
                matched_categories = []
                
                # Category keywords mapping
                category_keywords = {
                    'supply': ['توريد', 'supply', 'purchase', 'procurement'],
                    'services': ['خدمات', 'service', 'services'],
                    'construction': ['إنشاءات', 'construction', 'build', 'building', 'infrastructure'],
                    'maintenance': ['صيانة', 'تشغيل', 'maintenance', 'operation', 'operations'],
                    'consulting': ['استشارات', 'consulting', 'advisory', 'consultancy']
                }
                
                # Check each preferred category
                for category in categories_list:
                    if category in category_keywords:
                        keywords = category_keywords[category]
                        if any(keyword in type_lower for keyword in keywords):
                            matched_categories.append(category)
                
                if matched_categories:
                    score += 20
                    category_names = {
                        'supply': 'Supply',
                        'services': 'Services',
                        'construction': 'Construction',
                        'maintenance': 'Maintenance & Operation',
                        'consulting': 'Consulting'
                    }
                    matched_names = [category_names.get(c, c) for c in matched_categories]
                    reasons.append(f'Tender type matches category: {", ".join(matched_names)}')
            
            # Value range matching (20 points)
            if record.estimated_amount:
                if min_value <= record.estimated_amount <= max_value:
                    score += 20
                    reasons.append(f'Tender value ({record.estimated_amount:,.0f} SAR) within target range')
                elif record.estimated_amount < min_value:
                    # Below minimum - partial points
                    score += 5
                    reasons.append('Tender value below target range')
                elif record.estimated_amount > max_value:
                    # Above maximum - still interested but challenging
                    score += 10
                    reasons.append('Tender value above target range (challenging)')
            
            # Agency experience (15 points)
            # Check if agency is in preferred list OR we've won tenders from them
            if record.agency_name:
                agency_lower = record.agency_name.lower()
                
                # Check preferred agencies
                if agencies_list and any(pref in agency_lower or agency_lower in pref for pref in agencies_list):
                    score += 15
                    reasons.append(f'Agency "{record.agency_name}" is in preferred list')
                else:
                    # Check historical wins
                    won_count = self.search_count([
                        ('agency_name', '=', record.agency_name),
                        ('state', '=', 'won')
                    ])
                    if won_count > 0:
                        score += 15
                        reasons.append(f'Previous wins with {record.agency_name}')
            
            # Deadline availability (15 points)
            if record.remaining_days >= min_prep_days:
                score += 15
                reasons.append(f'Sufficient time to prepare ({record.remaining_days} days)')
            elif record.remaining_days >= (min_prep_days / 2):
                score += 8
                reasons.append(f'Limited time to prepare ({record.remaining_days} days)')
            elif record.remaining_days > 0:
                score += 3
                reasons.append(f'Very limited time ({record.remaining_days} days)')
            
            record.matching_score = min(100, score)  # Cap at 100
            record.matching_reasons = '\n'.join(reasons) if reasons else 'No matching criteria met'
    
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
    def fetch_etimad_tenders(self, page_size=20, page_number=1, max_pages=None):
        """Fetch tenders from Etimad platform with retry mechanism and pagination support
        
        Args:
            page_size: Number of tenders per page (default: 20, max: 50)
            page_number: Starting page number (default: 1)
            max_pages: Maximum number of pages to fetch (default: None = single page)
        
        Returns:
            Notification action dict with fetch results
        """
        session = self._setup_scraper_session()
        max_retries = 3
        total_created = 0
        total_updated = 0
        total_errors = 0
        pages_fetched = 0
        
        # First, visit the main portal to get cookies
        try:
            session.get("https://portal.etimad.sa/", timeout=10)
            time.sleep(2)
        except Exception as e:
            _logger.warning(f"Could not access portal homepage: {e}")
        
        # Determine if we're fetching multiple pages
        pages_to_fetch = [page_number] if not max_pages else list(range(page_number, page_number + max_pages))
        
        for current_page in pages_to_fetch:
            fetch_success = False
            
            for attempt in range(max_retries):
                try:
                    _logger.info(f"Fetching page {current_page}, attempt {attempt + 1}/{max_retries}...")
                    
                    timestamp = int(time.time() * 1000)
                    url = "https://tenders.etimad.sa/Tender/AllSupplierTendersForVisitorAsync"
                    
                    params = {
                        'PublishDateId': 5,  # Recent tenders
                        'PageSize': min(page_size, 50),  # Cap at 50
                        'PageNumber': current_page,
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
                            _logger.info(f"Successfully fetched {len(tenders)} tenders from page {current_page}")
                            
                            # Process tenders with error handling per tender
                            for tender_data in tenders:
                                try:
                                    is_new = self._process_tender_data(tender_data)
                                    if is_new:
                                        total_created += 1
                                    else:
                                        total_updated += 1
                                except Exception as e:
                                    total_errors += 1
                                    _logger.error(f"Error processing tender {tender_data.get('tenderIdString', 'unknown')}: {e}")
                            
                            pages_fetched += 1
                            fetch_success = True
                            
                            # Check if we got fewer results than page size (last page)
                            if max_pages and len(tenders) < page_size:
                                _logger.info("Reached last page with data")
                                break  # Exit pages_to_fetch loop
                            
                            break  # Exit retry loop
                        
                        except json.JSONDecodeError as e:
                            _logger.error(f"JSON decode error on page {current_page}: {e}")
                            if '<html' in response.text.lower():
                                raise UserError(_("Etimad portal is blocking requests. Please try again later."))
                    
                    time.sleep(3)
                    
                except requests.RequestException as e:
                    _logger.error(f"Request error for page {current_page} (attempt {attempt + 1}): {e}")
                    time.sleep(3)
            
            # If page fetch failed after all retries, log and continue
            if not fetch_success:
                _logger.error(f"Failed to fetch page {current_page} after {max_retries} attempts")
                total_errors += 1
            
            # Delay between pages to avoid rate limiting
            if current_page != pages_to_fetch[-1]:
                time.sleep(2)
        
        # Prepare result message
        if pages_fetched == 0:
            raise UserError(_("Failed to fetch any tenders. The site may have anti-bot protection."))
        
        message = _('%d created, %d updated') % (total_created, total_updated)
        if pages_fetched > 1:
            message += _(' from %d pages') % pages_fetched
        if total_errors > 0:
            message += _(' (%d errors)') % total_errors
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tenders Synchronized'),
                'message': message,
                'type': 'success' if total_errors == 0 else 'warning',
                'sticky': False,
            }
        }
    
    @api.model
    def action_fetch_batch(self):
        """Fetch multiple pages of tenders (batch operation)"""
        return self.fetch_etimad_tenders(page_size=50, page_number=1, max_pages=3)

    def _process_tender_data(self, raw_data):
        """Process and create/update tender record with improved error tracking"""
        
        try:
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
                # Scraping metadata
                'last_scraped_at': fields.Datetime.now(),
                'scraping_status': 'success',
                'scraping_error_count': 0,
                'last_scraping_error': False,
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
                
        except Exception as e:
            # Log error and update scraping status if tender exists
            _logger.error(f"Error processing tender data: {e}")
            tender_id = raw_data.get('tenderId')
            if tender_id:
                existing = self.search([('tender_id', '=', tender_id)], limit=1)
                if existing:
                    existing.write({
                        'scraping_status': 'failed',
                        'scraping_error_count': existing.scraping_error_count + 1,
                        'last_scraping_error': str(e),
                        'last_scraped_at': fields.Datetime.now(),
                    })
            raise
    
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
    
    def action_bulk_create_opportunities(self):
        """Bulk create opportunities for selected tenders"""
        created_count = 0
        existing_count = 0
        
        for record in self:
            if not record.opportunity_id:
                try:
                    record.action_create_opportunity()
                    created_count += 1
                except Exception as e:
                    _logger.error(f"Error creating opportunity for {record.name}: {e}")
            else:
                existing_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Operation Complete'),
                'message': _('%d opportunities created, %d already existed') % (created_count, existing_count),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_bulk_mark_as_progress(self):
        """Bulk mark selected tenders as in progress"""
        self.write({'state': 'in_progress'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Updated'),
                'message': _('%d tenders marked as in progress') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_bulk_mark_as_lost(self):
        """Bulk mark selected tenders as lost"""
        self.write({'state': 'lost'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Updated'),
                'message': _('%d tenders marked as lost') % len(self),
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_bulk_add_to_favorites(self):
        """Bulk add to favorites"""
        self.write({'is_favorite': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Favorites Updated'),
                'message': _('%d tenders added to favorites') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }

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
        """Fetch detailed tender information from all Etimad API endpoints"""
        self.ensure_one()
        
        if not self.tender_id_string:
            raise UserError(_('Tender ID String is required to fetch detailed information.'))
        
        try:
            session = self._setup_scraper_session()
            update_vals = {}
            fetched_count = 0
            
            # 1. Fetch Relations/Details
            try:
                url = "https://tenders.etimad.sa/Tender/GetRelationsDetailsViewComponenet"
                params = {'tenderIdStr': self.tender_id_string}
                response = session.get(url, params=params, timeout=30)
                
                if response.status_code == 200 and response.text:
                    parsed_data = self._parse_relations_details_html(response.text)
                    
                    # Classification
                    if parsed_data.get('classification_field'):
                        update_vals['classification_field'] = parsed_data['classification_field']
                        update_vals['classification_required'] = 'غير مطلوب' not in parsed_data['classification_field']
                    
                    # Execution location
                    if parsed_data.get('execution_location_type'):
                        update_vals['execution_location_type'] = parsed_data['execution_location_type']
                    if parsed_data.get('execution_regions'):
                        update_vals['execution_regions'] = parsed_data['execution_regions']
                    if parsed_data.get('execution_cities'):
                        update_vals['execution_cities'] = parsed_data['execution_cities']
                    
                    # Details
                    if parsed_data.get('details'):
                        update_vals['tender_purpose'] = parsed_data['details']
                    
                    # Activity details
                    if parsed_data.get('activity_details'):
                        update_vals['activity_details'] = parsed_data['activity_details']
                    
                    # Supply items
                    if parsed_data.get('includes_supply_items') is not None:
                        update_vals['includes_supply_items'] = parsed_data['includes_supply_items']
                    
                    # Construction works
                    if parsed_data.get('construction_works'):
                        update_vals['construction_works'] = parsed_data['construction_works']
                    
                    # Maintenance works
                    if parsed_data.get('maintenance_works'):
                        update_vals['maintenance_works'] = parsed_data['maintenance_works']
                    
                    fetched_count += 1
            except Exception as e:
                _logger.warning(f"Error fetching relations details: {e}")
            
            # 2. Fetch Dates
            try:
                url = "https://tenders.etimad.sa/Tender/GetTenderDatesViewComponenet"
                params = {'tenderIdStr': self.tender_id_string}
                response = session.get(url, params=params, timeout=30)
                
                if response.status_code == 200 and response.text:
                    dates_data = self._parse_dates_html(response.text)
                    
                    # Parse dates
                    if dates_data.get('last_enquiry_date'):
                        update_vals['last_enquiry_date'] = dates_data['last_enquiry_date']
                    if dates_data.get('offers_deadline'):
                        update_vals['offers_deadline'] = dates_data['offers_deadline']
                    if dates_data.get('offer_opening_date'):
                        update_vals['offer_opening_date'] = dates_data['offer_opening_date']
                    if dates_data.get('offer_examination_date'):
                        update_vals['offer_examination_date'] = dates_data['offer_examination_date']
                    if dates_data.get('expected_award_date'):
                        update_vals['expected_award_date'] = dates_data['expected_award_date']
                    if dates_data.get('work_start_date'):
                        update_vals['work_start_date'] = dates_data['work_start_date']
                    if dates_data.get('inquiry_start_date'):
                        update_vals['inquiry_start_date'] = dates_data['inquiry_start_date']
                    if dates_data.get('max_inquiry_response_days'):
                        update_vals['max_inquiry_response_days'] = dates_data['max_inquiry_response_days']
                    if dates_data.get('opening_location'):
                        update_vals['opening_location'] = dates_data['opening_location']
                    
                    fetched_count += 1
            except Exception as e:
                _logger.warning(f"Error fetching dates: {e}")
            
            # 3. Fetch Award Results
            try:
                url = "https://tenders.etimad.sa/Tender/GetAwardingResultsForVisitorViewComponenet"
                params = {'tenderIdStr': self.tender_id_string}
                response = session.get(url, params=params, timeout=30)
                
                if response.status_code == 200 and response.text:
                    award_data = self._parse_award_results_html(response.text)
                    
                    if award_data.get('award_announced') is not None:
                        update_vals['award_announced'] = award_data['award_announced']
                    if award_data.get('award_announcement_date'):
                        update_vals['award_announcement_date'] = award_data['award_announcement_date']
                    if award_data.get('awarded_company_name'):
                        update_vals['awarded_company_name'] = award_data['awarded_company_name']
                    if award_data.get('awarded_amount'):
                        update_vals['awarded_amount'] = award_data['awarded_amount']
                    
                    fetched_count += 1
            except Exception as e:
                _logger.warning(f"Error fetching award results: {e}")
            
            # Update tender with all fetched data
            if update_vals:
                self.write(update_vals)
                self.message_post(
                    body=_('Detailed information fetched from %d Etimad API endpoint(s).') % fetched_count,
                    subject=_('Details Updated')
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Detailed information has been fetched and updated from %d endpoint(s).') % fetched_count,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('No Updates'),
                        'message': _('No new information found to update.'),
                        'type': 'info',
                        'sticky': False,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error fetching detailed info: {e}")
            raise UserError(_('Error fetching detailed information: %s') % str(e))
    
    def _parse_relations_details_html(self, html_content):
        """Parse HTML content from GetRelationsDetailsViewComponenet API"""
        parsed_data = {}
        
        try:
            if LXML_AVAILABLE:
                # Use lxml for proper HTML parsing
                tree = html.fromstring(html_content)
                
                # Extract classification field
                classification_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "مجال التصنيف")]/following-sibling::div[1]//span/text()')
                if classification_elements:
                    classification_text = classification_elements[0].strip()
                    # Decode HTML entities
                    parsed_data['classification_field'] = html_module.unescape(classification_text)
                
                # Extract execution location type
                location_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "مكان التنفيذ")]/following-sibling::div[1]//span/text()')
                if location_elements:
                    location_text = html_module.unescape(location_elements[0].strip())
                    if 'داخل المملكة' in location_text:
                        parsed_data['execution_location_type'] = 'inside_kingdom'
                    elif 'خارج المملكة' in location_text:
                        parsed_data['execution_location_type'] = 'outside_kingdom'
                    else:
                        parsed_data['execution_location_type'] = 'both'
                
                # Extract regions and cities
                region_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "مكان التنفيذ")]/following-sibling::div[1]//ol/li/text()')
                city_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "مكان التنفيذ")]/following-sibling::div[1]//ul/li/text()')
                
                if region_elements:
                    regions = [html_module.unescape(r.strip()) for r in region_elements if r.strip()]
                    parsed_data['execution_regions'] = '\n'.join(regions)
                
                if city_elements:
                    cities = [html_module.unescape(c.strip()) for c in city_elements if c.strip()]
                    parsed_data['execution_cities'] = '\n'.join(cities)
                
                # Extract details
                details_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "التفاصيل")]/following-sibling::div[1]//span/text()')
                if details_elements:
                    parsed_data['details'] = html_module.unescape(details_elements[0].strip())
                
                # Extract activity details
                activity_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "نشاط المنافسة")]/following-sibling::div[1]//ol/li/text()')
                if activity_elements:
                    activities = [html_module.unescape(a.strip()) for a in activity_elements if a.strip()]
                    parsed_data['activity_details'] = '\n'.join(activities)
                
                # Extract supply items
                supply_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "تشمل المنافسة على بنود توريد")]/following-sibling::div[1]//span/text()')
                if supply_elements:
                    supply_text = html_module.unescape(supply_elements[0].strip())
                    parsed_data['includes_supply_items'] = 'لا' not in supply_text and ('نعم' in supply_text or 'yes' in supply_text.lower())
                
                # Extract construction works
                construction_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "أعمال الإنشاء")]/following-sibling::div[1]//ol/li/text()')
                if construction_elements:
                    construction_items = [html_module.unescape(c.strip()) for c in construction_elements if c.strip()]
                    if construction_items:
                        parsed_data['construction_works'] = '\n'.join(construction_items)
                
                # Extract maintenance works
                maintenance_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "أعمال الصيانة والتشغيل")]/following-sibling::div[1]//ol/li/text()')
                if maintenance_elements:
                    maintenance_items = [html_module.unescape(m.strip()) for m in maintenance_elements if m.strip()]
                    if maintenance_items:
                        parsed_data['maintenance_works'] = '\n'.join(maintenance_items)
            else:
                # Fallback to regex parsing if lxml not available
                parsed_data = self._parse_relations_details_regex(html_content)
                
        except Exception as e:
            _logger.error(f"Error parsing relations details HTML: {e}")
            # Fallback to regex parsing
            parsed_data = self._parse_relations_details_regex(html_content)
        
        return parsed_data
    
    def _parse_relations_details_regex(self, html_content):
        """Fallback regex-based parsing if lxml is not available"""
        parsed_data = {}
        
        try:
            # Extract classification field
            classification_match = re.search(r'مجال التصنيف.*?<span>\s*(.*?)\s*</span>', html_content, re.DOTALL)
            if classification_match:
                classification_text = re.sub(r'<[^>]+>', '', classification_match.group(1)).strip()
                parsed_data['classification_field'] = html_module.unescape(classification_text)
            
            # Extract execution location
            location_match = re.search(r'مكان التنفيذ.*?<span>\s*(.*?)\s*</span>', html_content, re.DOTALL)
            if location_match:
                location_text = html_module.unescape(re.sub(r'<[^>]+>', '', location_match.group(1)).strip())
                if 'داخل المملكة' in location_text:
                    parsed_data['execution_location_type'] = 'inside_kingdom'
                elif 'خارج المملكة' in location_text:
                    parsed_data['execution_location_type'] = 'outside_kingdom'
            
            # Extract regions (simplified)
            region_matches = re.findall(r'<li>\s*([^<]+?)\s*</li>', html_content)
            if region_matches:
                regions = [html_module.unescape(r.strip()) for r in region_matches if r.strip() and len(r.strip()) < 50]
                if regions:
                    parsed_data['execution_regions'] = '\n'.join(regions[:10])  # Limit to 10
            
            # Extract cities
            city_matches = re.findall(r'<ul>.*?<li>\s*([^<]+?)\s*</li>', html_content, re.DOTALL)
            if city_matches:
                cities = [html_module.unescape(c.strip()) for c in city_matches if c.strip() and len(c.strip()) < 50]
                if cities:
                    parsed_data['execution_cities'] = '\n'.join(cities[:20])  # Limit to 20
            
            # Extract details
            details_match = re.search(r'التفاصيل.*?<span>\s*(.*?)\s*</span>', html_content, re.DOTALL)
            if details_match:
                details_text = re.sub(r'<[^>]+>', '', details_match.group(1)).strip()
                parsed_data['details'] = html_module.unescape(details_text)
            
            # Extract activity details
            activity_matches = re.findall(r'نشاط المنافسة.*?<ol>(.*?)</ol>', html_content, re.DOTALL)
            if activity_matches:
                activity_items = re.findall(r'<li>([^<]+)</li>', activity_matches[0])
                if activity_items:
                    parsed_data['activity_details'] = '\n'.join([html_module.unescape(a.strip()) for a in activity_items])
            
            # Extract supply items
            supply_match = re.search(r'تشمل المنافسة على بنود توريد.*?<span>\s*(.*?)\s*</span>', html_content, re.DOTALL)
            if supply_match:
                supply_text = html_module.unescape(re.sub(r'<[^>]+>', '', supply_match.group(1)).strip())
                parsed_data['includes_supply_items'] = 'لا' not in supply_text and ('نعم' in supply_text or 'yes' in supply_text.lower())
            
            # Extract construction works
            construction_match = re.search(r'أعمال\s+الإنشاء.*?<ol>(.*?)</ol>', html_content, re.DOTALL)
            if construction_match:
                construction_items = re.findall(r'<li>([^<]+)</li>', construction_match.group(1))
                if construction_items:
                    parsed_data['construction_works'] = '\n'.join([html_module.unescape(c.strip()) for c in construction_items])
            
            # Extract maintenance works
            maintenance_match = re.search(r'أعمال\s+الصيانة.*?<ol>(.*?)</ol>', html_content, re.DOTALL)
            if maintenance_match:
                maintenance_items = re.findall(r'<li>([^<]+)</li>', maintenance_match.group(1))
                if maintenance_items:
                    parsed_data['maintenance_works'] = '\n'.join([html_module.unescape(m.strip()) for m in maintenance_items])
            
        except Exception as e:
            _logger.error(f"Error in regex parsing: {e}")
        
        return parsed_data
    
    def _parse_dates_html(self, html_content):
        """Parse HTML content from GetTenderDatesViewComponenet API"""
        parsed_data = {}
        
        try:
            if LXML_AVAILABLE:
                tree = html.fromstring(html_content)
                
                # Extract last enquiry date
                enquiry_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "آخر موعد لإستلام الإستفسارات")]/following-sibling::div[1]//span/text()')
                if enquiry_elements and len(enquiry_elements) > 0:
                    date_str = html_module.unescape(enquiry_elements[0].strip())
                    parsed_data['last_enquiry_date'] = self._parse_date_from_string(date_str)
                
                # Extract offers deadline
                deadline_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "آخر موعد لتقديم العروض")]/following-sibling::div[1]//span/text()')
                if deadline_elements and len(deadline_elements) > 0:
                    date_str = html_module.unescape(deadline_elements[0].strip())
                    time_str = ''
                    if len(deadline_elements) > 2:
                        time_str = html_module.unescape(deadline_elements[2].strip())
                    parsed_data['offers_deadline'] = self._parse_datetime_from_strings(date_str, time_str)
                
                # Extract offer opening date
                opening_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "تاريخ فتح العروض")]/following-sibling::div[1]//span/text()')
                if opening_elements:
                    opening_text = html_module.unescape(opening_elements[0].strip())
                    if 'لا يوجد' not in opening_text and opening_text.strip():
                        parsed_data['offer_opening_date'] = self._parse_date_from_string(opening_text)
                
                # Extract offer examination date
                examination_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "تاريخ فحص العروض")]/following-sibling::div[1]//span/text()')
                if examination_elements and len(examination_elements) > 0:
                    date_str = html_module.unescape(examination_elements[0].strip())
                    time_str = ''
                    if len(examination_elements) > 2:
                        time_str = html_module.unescape(examination_elements[2].strip())
                    parsed_data['offer_examination_date'] = self._parse_datetime_from_strings(date_str, time_str)
                
                # Extract expected award date
                award_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "التاريخ المتوقع للترسية")]/following-sibling::div[1]//span/text()')
                if award_elements and len(award_elements) > 0:
                    date_str = html_module.unescape(award_elements[0].strip())
                    parsed_data['expected_award_date'] = self._parse_date_from_string(date_str)
                
                # Extract work start date
                work_start_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "تاريخ بدء الأعمال")]/following-sibling::div[1]//span/text()')
                if work_start_elements and len(work_start_elements) > 0:
                    date_str = html_module.unescape(work_start_elements[0].strip())
                    parsed_data['work_start_date'] = self._parse_date_from_string(date_str)
                
                # Extract inquiry start date
                inquiry_start_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "بداية إرسال الأسئلة")]/following-sibling::div[1]//span/text()')
                if inquiry_start_elements and len(inquiry_start_elements) > 0:
                    date_str = html_module.unescape(inquiry_start_elements[0].strip())
                    parsed_data['inquiry_start_date'] = self._parse_date_from_string(date_str)
                
                # Extract max inquiry response days
                max_days_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "اقصى مدة للاجابة")]/following-sibling::div[1]//span/text()')
                if max_days_elements:
                    days_str = html_module.unescape(max_days_elements[0].strip())
                    try:
                        parsed_data['max_inquiry_response_days'] = int(days_str)
                    except ValueError:
                        pass
                
                # Extract opening location
                location_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "مكان فتح العرض")]/following-sibling::div[1]//span/text()')
                if location_elements:
                    location_text = html_module.unescape(location_elements[0].strip())
                    if 'لا يوجد' not in location_text:
                        parsed_data['opening_location'] = location_text
                
                # Extract offer opening date (تاريخ فحص العروض) - updated xpath
                examination_alt_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "تاريخ فحص العروض")]/following-sibling::div[1]//span/text()')
                if examination_alt_elements and len(examination_alt_elements) >= 3:
                    date_str = html_module.unescape(examination_alt_elements[0].strip())
                    time_str = html_module.unescape(examination_alt_elements[2].strip()) if len(examination_alt_elements) > 2 else ''
                    parsed_data['offer_examination_date'] = self._parse_datetime_from_strings(date_str, time_str)
            else:
                # Fallback to regex
                parsed_data = self._parse_dates_regex(html_content)
                
        except Exception as e:
            _logger.error(f"Error parsing dates HTML: {e}")
            parsed_data = self._parse_dates_regex(html_content)
        
        return parsed_data
    
    def _parse_dates_regex(self, html_content):
        """Fallback regex parsing for dates"""
        parsed_data = {}
        
        try:
            # Last enquiry date
            enquiry_match = re.search(r'آخر موعد لإستلام الإستفسارات.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            if enquiry_match:
                parsed_data['last_enquiry_date'] = self._parse_date_from_string(enquiry_match.group(1))
            
            # Offers deadline
            deadline_match = re.search(r'آخر موعد لتقديم العروض.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', html_content)
            if deadline_match:
                time_str = time_match.group(1) if time_match else ''
                parsed_data['offers_deadline'] = self._parse_datetime_from_strings(deadline_match.group(1), time_str)
            
            # Offer opening date
            opening_match = re.search(r'تاريخ فتح العروض.*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if opening_match:
                opening_text = html_module.unescape(re.sub(r'<[^>]+>', '', opening_match.group(1)).strip())
                if 'لا يوجد' not in opening_text and opening_text.strip():
                    parsed_data['offer_opening_date'] = self._parse_date_from_string(opening_text)
            
            # Examination date
            exam_match = re.search(r'تاريخ فحص العروض.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            exam_time_match = re.search(r'تاريخ فحص العروض.*?(\d{1,2}:\d{2}\s*(?:AM|PM))', html_content, re.DOTALL)
            if exam_match:
                time_str = exam_time_match.group(1) if exam_time_match else ''
                parsed_data['offer_examination_date'] = self._parse_datetime_from_strings(exam_match.group(1), time_str)
            
            # Expected award date
            award_match = re.search(r'التاريخ المتوقع للترسية.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            if award_match:
                parsed_data['expected_award_date'] = self._parse_date_from_string(award_match.group(1))
            
            # Work start date
            work_match = re.search(r'تاريخ بدء الأعمال.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            if work_match:
                parsed_data['work_start_date'] = self._parse_date_from_string(work_match.group(1))
            
            # Inquiry start date
            inquiry_match = re.search(r'بداية إرسال الأسئلة.*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            if inquiry_match:
                parsed_data['inquiry_start_date'] = self._parse_date_from_string(inquiry_match.group(1))
            
            # Max inquiry response days
            days_match = re.search(r'اقصى مدة للاجابة.*?<span>\s*(\d+)', html_content, re.DOTALL)
            if days_match:
                try:
                    parsed_data['max_inquiry_response_days'] = int(days_match.group(1))
                except ValueError:
                    pass
            
            # Opening location
            location_match = re.search(r'مكان فتح العرض.*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if location_match:
                parsed_data['opening_location'] = html_module.unescape(re.sub(r'<[^>]+>', '', location_match.group(1)).strip())
                
        except Exception as e:
            _logger.error(f"Error in regex dates parsing: {e}")
        
        return parsed_data
    
    def _parse_award_results_html(self, html_content):
        """Parse HTML content from GetAwardingResultsForVisitorViewComponenet API"""
        parsed_data = {}
        
        try:
            # Check if award has been announced
            if 'لم يتم اعلان نتائج الترسية بعد' in html_content or 'لم يتم' in html_content:
                parsed_data['award_announced'] = False
            else:
                # Try to extract award information if available
                parsed_data['award_announced'] = True
                
                if LXML_AVAILABLE:
                    tree = html.fromstring(html_content)
                    
                    # Extract award date, company, amount if available in the HTML
                    # (Structure may vary when award is announced)
                    award_date_elements = tree.xpath('//text()[contains(., "تاريخ")]/following::text()[1]')
                    company_elements = tree.xpath('//text()[contains(., "الشركة")]/following::text()[1]')
                    amount_elements = tree.xpath('//text()[contains(., "المبلغ")]/following::text()[1]')
                    
                    # This is a placeholder - actual structure may vary
                    # when award results are available
                    
        except Exception as e:
            _logger.error(f"Error parsing award results HTML: {e}")
            # Default to not announced if parsing fails
            parsed_data['award_announced'] = False
        
        return parsed_data
    
    def _parse_date_from_string(self, date_str):
        """Parse date string in DD/MM/YYYY format (Etimad format) to date object"""
        if not date_str or 'لا يوجد' in date_str or not date_str.strip():
            return False
        
        date_str = date_str.strip()
        
        try:
            # Try DD/MM/YYYY format (Etimad format)
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return date_obj.date()
        except ValueError:
            try:
                # Try other common formats
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d.%m.%Y']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # Fallback to existing _parse_date method for ISO formats
        parsed_datetime = self._parse_date(date_str)
        if parsed_datetime:
            return parsed_datetime.date()
        
        return False
    
    def _parse_datetime_from_strings(self, date_str, time_str=''):
        """Parse date and time strings to datetime object"""
        if not date_str or 'لا يوجد' in date_str:
            return False
        
        try:
            # Parse date
            date_obj = self._parse_date_from_string(date_str)
            if not date_obj:
                return False
            
            # Parse time if provided
            hour = 0
            minute = 0
            if time_str:
                time_str = time_str.strip().upper()
                # Handle AM/PM format
                if 'AM' in time_str or 'PM' in time_str:
                    time_part = time_str.replace('AM', '').replace('PM', '').strip()
                    if ':' in time_part:
                        hour, minute = map(int, time_part.split(':'))
                        if 'PM' in time_str and hour != 12:
                            hour += 12
                        elif 'AM' in time_str and hour == 12:
                            hour = 0
                else:
                    # Try HH:MM format
                    if ':' in time_str:
                        hour, minute = map(int, time_str.split(':'))
            
            return datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
        except Exception as e:
            _logger.warning(f"Error parsing datetime: {date_str} {time_str}, error: {e}")
            # Return just the date if time parsing fails
            return datetime.combine(self._parse_date_from_string(date_str), datetime.min.time()) if date_str else False
    
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
                    
                    # Get IDs of records in this recordset
                    record_ids = [r.id for r in self]
                    if record_ids:
                        if table_exists:
                            # Clean up only invalid references
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
                            # Table doesn't exist, clear all references
                            self.env.cr.execute("""
                                UPDATE ics_etimad_tender
                                SET tender_id_ics = NULL
                                WHERE id = ANY(%s)
                                AND tender_id_ics IS NOT NULL
                            """, (record_ids,))
                        
                        self.env.cr.commit()
                        _logger.info("Cleaned up invalid tender_id_ics references for records: %s", record_ids)
                except Exception as cleanup_error:
                    _logger.warning("Error cleaning up tender reference during read: %s", cleanup_error)
                    pass
                
                # Retry the read with cleaning context
                return self.with_context(_cleaning_tender_refs=True).read(fields=fields, load=load)
            else:
                # Re-raise if not related to tender_id_ics
                raise
    
    def web_read(self, specification):
        """Override web_read to handle invalid tender_id_ics references in list views"""
        try:
            return super(EtimadTender, self).web_read(specification)
        except (AttributeError, ValueError) as e:
            error_str = str(e).lower()
            if 'tender_id_ics' in error_str or '_unknown' in error_str or "display_name" in error_str:
                # Clean up invalid references
                try:
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
                            self.env.cr.execute("""
                                UPDATE ics_etimad_tender
                                SET tender_id_ics = NULL
                                WHERE id = ANY(%s)
                                AND tender_id_ics IS NOT NULL
                            """, (record_ids,))
                        
                        self.env.cr.commit()
                        _logger.info("Cleaned up invalid tender_id_ics references in web_read for records: %s", record_ids)
                except Exception as cleanup_error:
                    _logger.warning("Error cleaning up in web_read: %s", cleanup_error)
                
                # Retry with context to exclude tender_id_ics
                return self.with_context(_cleaning_tender_refs=True).web_read(specification)
            else:
                raise
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