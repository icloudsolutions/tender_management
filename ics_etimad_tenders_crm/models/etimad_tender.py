# -*- coding: utf-8 -*-
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
    
    # Status and Classification (from Etimad Portal)
    tender_status_id = fields.Integer("Tender Status ID", help="Status ID from Etimad portal")
    
    # CRM Integration
    opportunity_id = fields.Many2one('crm.lead', string="Opportunity", tracking=True)
    opportunity_count = fields.Integer("Opportunities", compute='_compute_opportunity_count')
    
    # Additional Info
    description = fields.Text("Description")
    notes = fields.Text("Internal Notes")
    is_favorite = fields.Boolean("Favorite", default=False)
    
    # Internal Tracking (not related to Etimad portal status)
    is_participating = fields.Boolean("Participating", default=False,
        help="Mark this if your company is preparing a quotation for this tender")
    tender_purpose = fields.Text("Tender Purpose", help="الغرض من المنافسة")
    
    # Hijri Dates (as text)
    last_enquiry_date_hijri = fields.Char("Last Enquiry Date (Hijri)")
    last_offer_date_hijri = fields.Char("Last Offer Date (Hijri)")
    
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
    
    # ========== LOCAL CONTENT (المحتوى المحلي) ==========
    # Saudi local content requirements and SME benefits
    local_content_required = fields.Boolean("Local Content Required", 
        help="Whether this tender has local content requirements (المحتوى المحلي)")
    local_content_percentage = fields.Float("Local Content %", 
        help="Minimum local content percentage required (نسبة المحتوى المحلي المطلوبة)")
    local_content_mechanism = fields.Char("Local Content Mechanism",
        help="Mechanism for calculating local content (آلية احتساب المحتوى المحلي)")
    
    # SME (Small & Medium Enterprises) Benefits
    sme_participation_allowed = fields.Boolean("SME Participation Allowed",
        help="Whether Small & Medium Enterprises can participate (مشاركة المنشآت الصغيرة والمتوسطة)")
    sme_price_preference = fields.Float("SME Price Preference %",
        help="Price preference given to SME participants (الأفضلية السعرية للمنشآت الصغيرة والمتوسطة)")
    sme_qualification_mandatory = fields.Boolean("SME Qualification Mandatory",
        help="Whether SME certificate is mandatory (شهادة المنشآت الصغيرة إلزامية)")
    
    # Additional Local Content Info
    local_content_target_percentage = fields.Float("Target Local Content %",
        help="Target percentage for local content evaluation (نسبة المحتوى المحلي المستهدفة للتقييم)")
    local_content_baseline_weight = fields.Float("Local Content Weight %",
        help="Weight of local content in evaluation (وزن المحتوى المحلي في التقييم)")
    local_content_notes = fields.Text("Local Content Notes",
        help="Additional notes about local content requirements")

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
    
    # ========== CHANGE TRACKING (Etimad Updates) ==========
    # Track previous values to detect changes from Etimad
    previous_offers_deadline = fields.Datetime("Previous Offers Deadline", readonly=True,
        help="Previous deadline before last update from Etimad")
    previous_last_enquiry_date = fields.Datetime("Previous Enquiry Deadline", readonly=True,
        help="Previous enquiry deadline before last update from Etimad")
    previous_estimated_amount = fields.Monetary("Previous Estimated Amount", currency_field='currency_id', readonly=True,
        help="Previous estimated amount before last update from Etimad")
    
    # Deadline extension tracking
    deadline_extended = fields.Boolean("Deadline Extended", default=False, readonly=True,
        help="True if offers deadline was extended since first scrape")
    deadline_extensions_count = fields.Integer("Extension Count", default=0, readonly=True,
        help="Number of times the deadline has been extended")
    last_deadline_extension_date = fields.Datetime("Last Extension Date", readonly=True,
        help="When the last deadline extension was detected")
    
    # Change log summary
    has_etimad_updates = fields.Boolean("Has Etimad Updates", default=False, readonly=True,
        help="True if tender has been updated from Etimad after initial creation")
    last_significant_change = fields.Text("Last Significant Change", readonly=True,
        help="Summary of last significant change from Etimad")
    change_notification_sent = fields.Boolean("Change Notification Sent", default=False,
        help="Whether users have been notified of the last change")
    
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
        """Process and create/update tender record with change detection and notifications"""
        
        try:
            # Map the raw data to Odoo fields
            new_offers_deadline = self._parse_date(raw_data.get('lastOfferPresentationDate'))
            new_enquiry_deadline = self._parse_date(raw_data.get('lastEnqueriesDate'))
            new_estimated_amount = float(raw_data.get('estimatedAmount', 0) or 0)
            
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
                'last_enquiry_date': new_enquiry_deadline,
                'offers_deadline': new_offers_deadline,
                'submission_date': self._parse_date(raw_data.get('submitionDate')),
                'invitation_cost': float(raw_data.get('invitationCost', 0) or 0),
                'financial_fees': float(raw_data.get('financialFees', 0) or 0),
                'estimated_amount': new_estimated_amount,
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
            
            # No need to map status - we keep Etimad portal status as-is
            
            # Check if tender already exists
            existing = self.search([
                '|',
                ('reference_number', '=', vals['reference_number']),
                ('tender_id', '=', vals['tender_id'])
            ], limit=1)
            
            if existing:
                # CHANGE DETECTION - Track what changed from Etimad
                changes = []
                
                # Check deadline extension
                if new_offers_deadline and existing.offers_deadline:
                    if new_offers_deadline > existing.offers_deadline:
                        days_extended = (new_offers_deadline - existing.offers_deadline).days
                        changes.append(f"⏰ Offers deadline EXTENDED by {days_extended} days (new: {new_offers_deadline.strftime('%Y-%m-%d %H:%M')})")
                        vals['previous_offers_deadline'] = existing.offers_deadline
                        vals['deadline_extended'] = True
                        vals['deadline_extensions_count'] = existing.deadline_extensions_count + 1
                        vals['last_deadline_extension_date'] = fields.Datetime.now()
                    elif new_offers_deadline < existing.offers_deadline:
                        days_reduced = (existing.offers_deadline - new_offers_deadline).days
                        changes.append(f"⚠️ Offers deadline REDUCED by {days_reduced} days (new: {new_offers_deadline.strftime('%Y-%m-%d %H:%M')})")
                        vals['previous_offers_deadline'] = existing.offers_deadline
                
                # Check enquiry deadline changes
                if new_enquiry_deadline and existing.last_enquiry_date:
                    if new_enquiry_deadline != existing.last_enquiry_date:
                        changes.append(f"📝 Enquiry deadline changed to {new_enquiry_deadline.strftime('%Y-%m-%d %H:%M')}")
                        vals['previous_last_enquiry_date'] = existing.last_enquiry_date
                
                # Check estimated amount changes
                if new_estimated_amount and existing.estimated_amount:
                    if abs(new_estimated_amount - existing.estimated_amount) > 1000:  # Significant if > 1000 SAR
                        change_pct = ((new_estimated_amount - existing.estimated_amount) / existing.estimated_amount) * 100
                        changes.append(f"💰 Estimated amount changed: {existing.estimated_amount:,.0f} → {new_estimated_amount:,.0f} SAR ({change_pct:+.1f}%)")
                        vals['previous_estimated_amount'] = existing.estimated_amount
                
                # Update record with change tracking
                if changes:
                    vals['has_etimad_updates'] = True
                    vals['last_significant_change'] = '\n'.join(changes)
                    vals['change_notification_sent'] = False  # Reset so users can be notified
                    
                    # Post to chatter
                    existing.sudo().write(vals)
                    existing.message_post(
                        body=f"<strong>🔄 Etimad Tender Updated</strong><br/><br/>{'<br/>'.join(changes)}",
                        subject='Etimad Update Detected',
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                    
                    # Create activity for deadline extension (important!)
                    if 'deadline_extended' in vals and vals['deadline_extended']:
                        existing._create_deadline_extension_activity(vals.get('previous_offers_deadline'), new_offers_deadline)
                    
                    _logger.info(f"Updated tender with changes: {vals['name'][:50]}")
                else:
                    # No significant changes, just update scraping metadata
                    existing.write(vals)
                    _logger.info(f"Updated tender (no significant changes): {vals['name'][:50]}")
                
                return False
            else:
                # New tender
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
    
    def _create_deadline_extension_activity(self, old_deadline, new_deadline):
        """Create activity to alert users about deadline extension"""
        self.ensure_one()
        days_extended = (new_deadline - old_deadline).days
        
        # Create activity for responsible user or tender team
        activity_user = self.env.user
        if self.opportunity_id and self.opportunity_id.user_id:
            activity_user = self.opportunity_id.user_id
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=f'Deadline Extended: {self.name[:50]}',
            note=f'''
                <p><strong>Good News! The tender deadline has been extended.</strong></p>
                <ul>
                    <li><strong>Tender:</strong> {self.name}</li>
                    <li><strong>Agency:</strong> {self.agency_name}</li>
                    <li><strong>Previous Deadline:</strong> {old_deadline.strftime("%Y-%m-%d %H:%M")}</li>
                    <li><strong>New Deadline:</strong> {new_deadline.strftime("%Y-%m-%d %H:%M")}</li>
                    <li><strong>Extended by:</strong> {days_extended} days</li>
                </ul>
                <p>You now have more time to prepare your quotation.</p>
                <p><a href="/web#id={self.id}&model=ics.etimad.tender">View Tender</a></p>
            ''',
            user_id=activity_user.id,
        )
    
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

    def action_toggle_participating(self):
        """Toggle participation status"""
        self.ensure_one()
        self.is_participating = not self.is_participating
        if self.is_participating:
            self.message_post(body=_('✅ Marked as participating in this tender'))
        else:
            self.message_post(body=_('⬜ Unmarked as participating'))
    
    def action_fetch_detailed_info(self):
        # Fetch detailed tender information from all Etimad API endpoints
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
            
            # 4. Fetch Local Content Details (المحتوى المحلي)
            try:
                url = "https://tenders.etimad.sa/Tender/GetLocalContentDetailsViewComponenet"
                params = {'tenderIdStr': self.tender_id_string}
                response = session.get(url, params=params, timeout=30)
                
                if response.status_code == 200 and response.text:
                    local_content_data = self._parse_local_content_html(response.text)
                    
                    if local_content_data.get('local_content_required') is not None:
                        update_vals['local_content_required'] = local_content_data['local_content_required']
                    if local_content_data.get('local_content_percentage'):
                        update_vals['local_content_percentage'] = local_content_data['local_content_percentage']
                    if local_content_data.get('local_content_mechanism'):
                        update_vals['local_content_mechanism'] = local_content_data['local_content_mechanism']
                    if local_content_data.get('local_content_target_percentage'):
                        update_vals['local_content_target_percentage'] = local_content_data['local_content_target_percentage']
                    if local_content_data.get('local_content_baseline_weight'):
                        update_vals['local_content_baseline_weight'] = local_content_data['local_content_baseline_weight']
                    if local_content_data.get('sme_participation_allowed') is not None:
                        update_vals['sme_participation_allowed'] = local_content_data['sme_participation_allowed']
                    if local_content_data.get('sme_price_preference'):
                        update_vals['sme_price_preference'] = local_content_data['sme_price_preference']
                    if local_content_data.get('sme_qualification_mandatory') is not None:
                        update_vals['sme_qualification_mandatory'] = local_content_data['sme_qualification_mandatory']
                    if local_content_data.get('local_content_notes'):
                        update_vals['local_content_notes'] = local_content_data['local_content_notes']
                    
                    fetched_count += 1
            except Exception as e:
                _logger.warning(f"Error fetching local content details: {e}")
            
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
            # Multiple variations of "no award yet" message
            no_award_phrases = [
                'لم يتم اعلان نتائج الترسية بعد',
                'لم يتم الإعلان عن نتائج الترسية',
                'لم يتم',  # Partial match
                'Award results have not been announced yet',
                'No award results',
                'لا توجد نتائج',  # No results
                'لا يوجد'  # Does not exist
            ]
            
            # Check for any "no award" indicator
            has_no_award_message = any(phrase in html_content for phrase in no_award_phrases)
            
            # Additional check: if HTML is very short, likely means no data
            if len(html_content.strip()) < 100 or has_no_award_message:
                parsed_data['award_announced'] = False
                return parsed_data
            
            # Award has been announced - extract details
            parsed_data['award_announced'] = True
            
            if LXML_AVAILABLE:
                tree = html.fromstring(html_content)
                
                # Extract award announcement date
                # Look for "تاريخ الاعلان" or "Announcement Date"
                date_elements = tree.xpath('//div[contains(@class, "etd-item-title") and (contains(text(), "تاريخ الاعلان") or contains(text(), "تاريخ الإعلان"))]/following-sibling::div[1]//span/text()')
                if date_elements:
                    date_str = html_module.unescape(date_elements[0].strip())
                    parsed_data['award_announcement_date'] = self._parse_date_from_string(date_str)
                
                # Extract awarded company name
                # Look for "اسم الشركة المرسية" or "Awarded Company"
                company_elements = tree.xpath('//div[contains(@class, "etd-item-title") and (contains(text(), "الشركة") or contains(text(), "المورد"))]/following-sibling::div[1]//span/text()')
                if company_elements:
                    company_name = html_module.unescape(company_elements[0].strip())
                    if company_name and 'لا يوجد' not in company_name:
                        parsed_data['awarded_company_name'] = company_name
                
                # Extract awarded amount
                # Look for "المبلغ" or "Amount"
                amount_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "المبلغ")]/following-sibling::div[1]//span/text()')
                if amount_elements:
                    amount_str = html_module.unescape(amount_elements[0].strip())
                    # Remove commas and currency symbols, extract number
                    amount_str = re.sub(r'[^\d.]', '', amount_str)
                    try:
                        if amount_str:
                            parsed_data['awarded_amount'] = float(amount_str)
                    except ValueError:
                        pass
                
                # Alternative: Try table structure for award results
                # Some tenders display results in a table format
                rows = tree.xpath('//table//tr')
                for row in rows:
                    cells = row.xpath('.//td//text()')
                    if len(cells) >= 2:
                        # Check if row contains company/amount info
                        for i, cell in enumerate(cells):
                            cell_text = html_module.unescape(cell.strip())
                            if 'شركة' in cell_text or 'مؤسسة' in cell_text:
                                # Next cell might be company name or amount
                                if i + 1 < len(cells):
                                    next_cell = html_module.unescape(cells[i + 1].strip())
                                    if next_cell and 'لا يوجد' not in next_cell:
                                        if not parsed_data.get('awarded_company_name'):
                                            parsed_data['awarded_company_name'] = next_cell
            else:
                # Fallback to regex parsing
                parsed_data.update(self._parse_award_results_regex(html_content))
            
            # Final check: If award_announced is True but no actual data extracted, set to False
            if parsed_data.get('award_announced') and not any([
                parsed_data.get('award_announcement_date'),
                parsed_data.get('awarded_company_name'),
                parsed_data.get('awarded_amount')
            ]):
                # Announced but no data found - probably false positive
                _logger.warning("Award announced flag set but no award data extracted - likely no award yet")
                parsed_data['award_announced'] = False
                    
        except Exception as e:
            _logger.error(f"Error parsing award results HTML: {e}")
            # Try regex fallback
            try:
                parsed_data.update(self._parse_award_results_regex(html_content))
            except:
                parsed_data['award_announced'] = False
        
        return parsed_data
    
    def _parse_award_results_regex(self, html_content):
        """Fallback regex parsing for award results"""
        parsed_data = {'award_announced': True}
        
        try:
            # Extract company name
            company_match = re.search(r'(?:الشركة|المورد).*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if company_match:
                company_name = html_module.unescape(re.sub(r'<[^>]+>', '', company_match.group(1)).strip())
                if company_name and 'لا يوجد' not in company_name:
                    parsed_data['awarded_company_name'] = company_name
            
            # Extract amount
            amount_match = re.search(r'المبلغ.*?<span>\s*([0-9,.]+)', html_content, re.DOTALL)
            if amount_match:
                amount_str = re.sub(r'[^\d.]', '', amount_match.group(1))
                try:
                    if amount_str:
                        parsed_data['awarded_amount'] = float(amount_str)
                except ValueError:
                    pass
            
            # Extract date
            date_match = re.search(r'تاريخ.*?(?:الإعلان|الاعلان).*?<span>\s*(\d{2}/\d{2}/\d{4})', html_content, re.DOTALL)
            if date_match:
                parsed_data['award_announcement_date'] = self._parse_date_from_string(date_match.group(1))
                
        except Exception as e:
            _logger.error(f"Error in regex award parsing: {e}")
        
        return parsed_data
    
    def _parse_local_content_html(self, html_content):
        """Parse HTML content from GetLocalContentDetailsViewComponenet API"""
        parsed_data = {}
        
        try:
            # Check if local content requirements exist
            if 'لا توجد بيانات' in html_content or 'No data available' in html_content:
                parsed_data['local_content_required'] = False
                return parsed_data
            
            parsed_data['local_content_required'] = True
            
            if LXML_AVAILABLE:
                tree = html.fromstring(html_content)
                
                # Extract minimum local content percentage
                # Look for "نسبة المحتوى المحلي الدنيا" or "Minimum Local Content %"
                percentage_elements = tree.xpath('//div[contains(@class, "etd-item-title") and (contains(text(), "نسبة المحتوى المحلي") or contains(text(), "المحتوى المحلي الدنيا"))]/following-sibling::div[1]//span/text()')
                if percentage_elements:
                    percentage_str = html_module.unescape(percentage_elements[0].strip())
                    # Extract number from text like "30%" or "30 %" or "30"
                    percentage_match = re.search(r'(\d+(?:\.\d+)?)', percentage_str)
                    if percentage_match:
                        parsed_data['local_content_percentage'] = float(percentage_match.group(1))
                
                # Extract local content mechanism
                # Look for "آلية احتساب المحتوى المحلي"
                mechanism_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "آلية احتساب")]/following-sibling::div[1]//span/text()')
                if mechanism_elements:
                    mechanism_text = html_module.unescape(mechanism_elements[0].strip())
                    if mechanism_text and 'لا يوجد' not in mechanism_text:
                        parsed_data['local_content_mechanism'] = mechanism_text
                
                # Extract target percentage for evaluation
                # Look for "نسبة المحتوى المحلي المستهدفة للتقييم"
                target_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "المستهدفة للتقييم")]/following-sibling::div[1]//span/text()')
                if target_elements:
                    target_str = html_module.unescape(target_elements[0].strip())
                    target_match = re.search(r'(\d+(?:\.\d+)?)', target_str)
                    if target_match:
                        parsed_data['local_content_target_percentage'] = float(target_match.group(1))
                
                # Extract local content weight in evaluation
                # Look for "وزن المحتوى المحلي"
                weight_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "وزن المحتوى المحلي")]/following-sibling::div[1]//span/text()')
                if weight_elements:
                    weight_str = html_module.unescape(weight_elements[0].strip())
                    weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_str)
                    if weight_match:
                        parsed_data['local_content_baseline_weight'] = float(weight_match.group(1))
                
                # Extract SME (Small & Medium Enterprises) participation
                # Look for "مشاركة المنشآت الصغيرة والمتوسطة"
                sme_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "المنشآت الصغيرة")]/following-sibling::div[1]//span/text()')
                if sme_elements:
                    sme_text = html_module.unescape(sme_elements[0].strip()).lower()
                    parsed_data['sme_participation_allowed'] = 'نعم' in sme_text or 'yes' in sme_text or 'مسموح' in sme_text
                
                # Extract SME price preference
                # Look for "الأفضلية السعرية"
                sme_preference_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "الأفضلية السعرية")]/following-sibling::div[1]//span/text()')
                if sme_preference_elements:
                    preference_str = html_module.unescape(sme_preference_elements[0].strip())
                    preference_match = re.search(r'(\d+(?:\.\d+)?)', preference_str)
                    if preference_match:
                        parsed_data['sme_price_preference'] = float(preference_match.group(1))
                
                # Extract SME qualification mandatory
                # Look for "شهادة المنشآت" or "SME Certificate"
                sme_cert_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "شهادة المنشآت")]/following-sibling::div[1]//span/text()')
                if sme_cert_elements:
                    cert_text = html_module.unescape(sme_cert_elements[0].strip()).lower()
                    parsed_data['sme_qualification_mandatory'] = 'إلزامي' in cert_text or 'mandatory' in cert_text or 'مطلوب' in cert_text
                
                # Collect any additional notes about local content
                notes_elements = tree.xpath('//div[contains(@class, "etd-item-title") and contains(text(), "ملاحظات")]/following-sibling::div[1]//span/text()')
                if notes_elements:
                    notes_text = html_module.unescape(notes_elements[0].strip())
                    if notes_text and 'لا يوجد' not in notes_text:
                        parsed_data['local_content_notes'] = notes_text
            else:
                # Fallback to regex parsing
                parsed_data.update(self._parse_local_content_regex(html_content))
                
        except Exception as e:
            _logger.error(f"Error parsing local content HTML: {e}")
            try:
                parsed_data.update(self._parse_local_content_regex(html_content))
            except:
                parsed_data['local_content_required'] = False
        
        return parsed_data
    
    def _parse_local_content_regex(self, html_content):
        """Fallback regex parsing for local content"""
        parsed_data = {'local_content_required': True}
        
        try:
            # Extract minimum percentage
            percentage_match = re.search(r'(?:نسبة المحتوى المحلي|المحتوى المحلي الدنيا).*?<span>\s*(\d+(?:\.\d+)?)', html_content, re.DOTALL)
            if percentage_match:
                parsed_data['local_content_percentage'] = float(percentage_match.group(1))
            
            # Extract mechanism
            mechanism_match = re.search(r'آلية احتساب.*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if mechanism_match:
                mechanism_text = html_module.unescape(re.sub(r'<[^>]+>', '', mechanism_match.group(1)).strip())
                if mechanism_text and 'لا يوجد' not in mechanism_text:
                    parsed_data['local_content_mechanism'] = mechanism_text
            
            # Extract target percentage
            target_match = re.search(r'المستهدفة للتقييم.*?<span>\s*(\d+(?:\.\d+)?)', html_content, re.DOTALL)
            if target_match:
                parsed_data['local_content_target_percentage'] = float(target_match.group(1))
            
            # Extract weight
            weight_match = re.search(r'وزن المحتوى المحلي.*?<span>\s*(\d+(?:\.\d+)?)', html_content, re.DOTALL)
            if weight_match:
                parsed_data['local_content_baseline_weight'] = float(weight_match.group(1))
            
            # Extract SME participation
            sme_match = re.search(r'المنشآت الصغيرة.*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if sme_match:
                sme_text = html_module.unescape(re.sub(r'<[^>]+>', '', sme_match.group(1)).strip()).lower()
                parsed_data['sme_participation_allowed'] = 'نعم' in sme_text or 'yes' in sme_text
            
            # Extract SME price preference
            preference_match = re.search(r'الأفضلية السعرية.*?<span>\s*(\d+(?:\.\d+)?)', html_content, re.DOTALL)
            if preference_match:
                parsed_data['sme_price_preference'] = float(preference_match.group(1))
            
            # Extract SME mandatory
            cert_match = re.search(r'شهادة المنشآت.*?<span>\s*([^<]+?)\s*</span>', html_content, re.DOTALL)
            if cert_match:
                cert_text = html_module.unescape(re.sub(r'<[^>]+>', '', cert_match.group(1)).strip()).lower()
                parsed_data['sme_qualification_mandatory'] = 'إلزامي' in cert_text or 'مطلوب' in cert_text
                
        except Exception as e:
            _logger.error(f"Error in regex local content parsing: {e}")
        
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
    