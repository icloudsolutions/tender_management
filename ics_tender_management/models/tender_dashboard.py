# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class IcsTenderDashboard(models.Model):
    _name = 'ics.tender.dashboard'
    _description = "ICS Tender Dashboard"

    name = fields.Char(string="Dashboard", default="Tender Dashboard")

    @api.model
    def get_tender_statistics(self):
        """Get comprehensive tender statistics for dashboard"""
        tender_obj = self.env['ics.tender.management']

        total_tenders = tender_obj.search_count([])

        draft_tenders = tender_obj.search_count([('stage_id.sequence', '=', 1)])
        active_tenders = tender_obj.search_count([
            ('stage_id.name', 'in', ['Vendor Selection', 'Quotation Preparation', 'Quotation Review'])
        ])
        won_tenders = tender_obj.search_count([('stage_id.name', '=', 'Won')])
        lost_tenders = tender_obj.search_count([('stage_id.name', '=', 'Lost')])

        supply_projects = tender_obj.search_count([('tender_category', '=', 'supply')])
        maintenance_projects = tender_obj.search_count([('tender_category', '=', 'maintenance')])

        vendor_offers = self._get_vendor_offer_stats()
        tender_by_category = self._get_tender_by_category()
        tender_by_type = self._get_tender_by_type()
        monthly_trend = self._get_monthly_trend()
        etimad_stats = self._get_etimad_statistics()
        stage_distribution = self._get_stage_distribution()
        financial_summary = self._get_financial_summary()

        return {
            'total_tenders': total_tenders,
            'draft_tenders': draft_tenders,
            'active_tenders': active_tenders,
            'won_tenders': won_tenders,
            'lost_tenders': lost_tenders,
            'supply_projects': supply_projects,
            'maintenance_projects': maintenance_projects,
            'vendor_offers': vendor_offers,
            'tender_by_category': tender_by_category,
            'tender_by_type': tender_by_type,
            'monthly_trend': monthly_trend,
            'etimad_stats': etimad_stats,
            'stage_distribution': stage_distribution,
            'financial_summary': financial_summary,
        }

    def _get_vendor_offer_stats(self):
        """Get vendor offer statistics"""
        tender_obj = self.env['ics.tender.management']

        total_offers = 0
        pending_offers = 0
        accepted_offers = 0

        all_tenders = tender_obj.search([])
        for tender in all_tenders:
            if tender.tender_type == 'single_vendor':
                total_offers += len(tender.vendor_offer_ids)
                pending_offers += len(tender.vendor_offer_ids.filtered(lambda o: o.status == 'pending'))
                accepted_offers += len(tender.vendor_offer_ids.filtered(lambda o: o.status == 'accepted'))
            else:
                for line in tender.boq_line_ids:
                    total_offers += len(line.vendor_offer_ids)
                    pending_offers += len(line.vendor_offer_ids.filtered(lambda o: o.status == 'pending'))
                    accepted_offers += len(line.vendor_offer_ids.filtered(lambda o: o.status == 'accepted'))

        return {
            'total': total_offers,
            'pending': pending_offers,
            'accepted': accepted_offers,
        }

    def _get_tender_by_category(self):
        """Get tender distribution by category"""
        tender_obj = self.env['ics.tender.management']

        categories = [
            ('supply', 'Supply Projects'),
            ('services', 'Professional Services'),
            ('construction', 'Construction'),
            ('maintenance', 'Maintenance & Operations'),
            ('it', 'IT Equipment & Software'),
        ]

        labels = []
        values = []

        for cat_code, cat_name in categories:
            count = tender_obj.search_count([('tender_category', '=', cat_code)])
            if count > 0:
                labels.append(cat_name)
                values.append(count)

        return {
            'labels': labels,
            'values': values
        }

    def _get_tender_by_type(self):
        """Get tender distribution by tender type"""
        tender_obj = self.env['ics.tender.management']

        single_vendor = tender_obj.search_count([('tender_type', '=', 'single_vendor')])
        multiple_vendor = tender_obj.search_count([('tender_type', '=', 'multiple_vendor')])

        return {
            'labels': ['Single Vendor', 'Product-wise Vendor'],
            'values': [single_vendor, multiple_vendor]
        }

    def _get_monthly_trend(self):
        """Get tender creation trend for last 6 months"""
        tender_obj = self.env['ics.tender.management']

        months = []
        values = []

        today = datetime.today()

        for i in range(5, -1, -1):
            month_start = (today - relativedelta(months=i)).replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

            count = tender_obj.search_count([
                ('create_date', '>=', month_start.strftime('%Y-%m-%d')),
                ('create_date', '<=', month_end.strftime('%Y-%m-%d'))
            ])

            months.append(month_start.strftime('%B'))
            values.append(count)

        return {
            'labels': months,
            'values': values
        }

    def _get_etimad_statistics(self):
        """Get Etimad integration statistics"""
        etimad_obj = self.env.get('ics.etimad.tender')

        if not etimad_obj:
            return {
                'total_etimad': 0,
                'new_tenders': 0,
                'imported_tenders': 0,
            }

        total_etimad = etimad_obj.search_count([])
        new_tenders = etimad_obj.search_count([('status', '=', 'new')])
        imported_tenders = etimad_obj.search_count([('is_imported', '=', True)])

        return {
            'total_etimad': total_etimad,
            'new_tenders': new_tenders,
            'imported_tenders': imported_tenders,
        }

    def _get_stage_distribution(self):
        """Get tender distribution by stage"""
        tender_obj = self.env['ics.tender.management']
        stage_obj = self.env['ics.tender.stage']

        stages = stage_obj.search([('name', 'not in', ['Draft', 'Won', 'Lost'])], order='sequence')

        labels = []
        values = []

        for stage in stages:
            count = tender_obj.search_count([('stage_id', '=', stage.id)])
            if count > 0:
                labels.append(stage.name)
                values.append(count)

        return {
            'labels': labels,
            'values': values
        }

    def _get_financial_summary(self):
        """Get financial summary of tenders"""
        tender_obj = self.env['ics.tender.management']

        all_tenders = tender_obj.search([])

        total_budget = sum(tender.estimated_cost or 0 for tender in all_tenders)
        active_budget = sum(
            tender.estimated_cost or 0
            for tender in all_tenders
            if tender.stage_id.name in ['Vendor Selection', 'Quotation Preparation', 'Quotation Review']
        )
        won_budget = sum(
            tender.final_total or 0
            for tender in all_tenders
            if tender.stage_id.name == 'Won'
        )

        return {
            'total_budget': total_budget,
            'active_budget': active_budget,
            'won_budget': won_budget,
            'currency_symbol': self.env.company.currency_id.symbol or 'SAR',
        }
