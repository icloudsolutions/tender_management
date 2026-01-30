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
        tender_obj = self.env['ics.tender']

        total_tenders = tender_obj.search_count([])

        # Use the workflow field on the tender (Odoo 18 compatible; no stage flags required)
        draft_tenders = tender_obj.search_count([('state', '=', 'draft')])
        active_tenders = tender_obj.search_count([('state', 'in', ['technical', 'financial', 'quotation', 'submitted', 'evaluation'])])
        won_tenders = tender_obj.search_count([('state', '=', 'won')])
        lost_tenders = tender_obj.search_count([('state', '=', 'lost')])

        supply_projects = tender_obj.search_count([('tender_category', '=', 'supply')])
        maintenance_projects = tender_obj.search_count([('tender_category', '=', 'maintenance')])

        vendor_offers = self._get_vendor_offer_stats()
        tender_by_category = self._get_tender_by_category()
        tender_by_type = self._get_tender_by_type()
        monthly_trend = self._get_monthly_trend()
        etimad_stats = self._get_etimad_statistics()
        stage_distribution = self._get_stage_distribution()
        financial_summary = self._get_financial_summary()
        project_execution = self._get_project_execution_stats()
        procedure_compliance = self._get_procedure_compliance()
        win_loss_ratio = self._get_win_loss_ratio()

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
            'project_execution': project_execution,
            'procedure_compliance': procedure_compliance,
            'win_loss_ratio': win_loss_ratio,
        }

    def _get_vendor_offer_stats(self):
        """Get vendor offer statistics"""
        tender_obj = self.env['ics.tender']

        total_offers = 0
        accepted_offers = 0

        all_tenders = tender_obj.search([])
        for tender in all_tenders:
            # Offers exist on BoQ lines in this module
            for line in tender.boq_line_ids:
                offers = line.vendor_offer_ids
                total_offers += len(offers)
                # Treat "accepted" as the selected vendor offer
                accepted_offers += len(offers.filtered(lambda o: o.is_selected))

        pending_offers = max(total_offers - accepted_offers, 0)

        return {
            'total': total_offers,
            'pending': pending_offers,
            'accepted': accepted_offers,
        }

    def _get_tender_by_category(self):
        """Get tender distribution by category"""
        tender_obj = self.env['ics.tender']

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
        tender_obj = self.env['ics.tender']

        single_vendor = tender_obj.search_count([('tender_type', '=', 'single_vendor')])
        product_wise = tender_obj.search_count([('tender_type', '=', 'product_wise')])

        return {
            'labels': ['Single Vendor', 'Product-wise Vendor'],
            'values': [single_vendor, product_wise]
        }

    def _get_monthly_trend(self):
        """Get tender creation trend for last 6 months"""
        tender_obj = self.env['ics.tender']

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
        tender_obj = self.env['ics.tender']
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
        tender_obj = self.env['ics.tender']

        all_tenders = tender_obj.search([])

        total_budget = sum(t.total_estimated_cost or 0 for t in all_tenders)
        active_budget = sum(
            (t.total_estimated_cost or 0)
            for t in all_tenders
            if t.state in ['technical', 'financial', 'quotation', 'submitted', 'evaluation']
        )
        won_budget = sum(
            (t.actual_revenue or t.total_quotation_amount or 0)
            for t in all_tenders
            if t.state == 'won'
        )

        return {
            'total_budget': total_budget,
            'active_budget': active_budget,
            'won_budget': won_budget,
            'currency_symbol': self.env.company.currency_id.symbol or 'SAR',
        }

    def _get_project_execution_stats(self):
        """Get project execution statistics for won tenders"""
        tender_obj = self.env['ics.tender']
        project_obj = self.env['project.project']

        won_tenders = tender_obj.search([('state', '=', 'won')])

        total_projects = project_obj.search_count([('tender_id', 'in', won_tenders.ids)])

        # Be defensive: some databases don't have project "closed" fields.
        in_execution = 0
        completed = 0
        supply_in_execution = 0
        maintenance_in_execution = 0

        # If project has a stage_id with an is_closed flag, use it; otherwise leave 0/0.
        if 'stage_id' in project_obj._fields:
            stage_model = project_obj._fields['stage_id'].comodel_name
            if stage_model and 'is_closed' in self.env[stage_model]._fields:
                in_execution = project_obj.search_count([('tender_id', 'in', won_tenders.ids), ('stage_id.is_closed', '=', False)])
                completed = project_obj.search_count([('tender_id', 'in', won_tenders.ids), ('stage_id.is_closed', '=', True)])
                supply_in_execution = project_obj.search_count([
                    ('tender_id.tender_category', '=', 'supply'),
                    ('tender_id', 'in', won_tenders.ids),
                    ('stage_id.is_closed', '=', False),
                ])
                maintenance_in_execution = project_obj.search_count([
                    ('tender_id.tender_category', '=', 'maintenance'),
                    ('tender_id', 'in', won_tenders.ids),
                    ('stage_id.is_closed', '=', False),
                ])

        return {
            'total_projects': total_projects,
            'in_execution': in_execution,
            'completed': completed,
            'supply_in_execution': supply_in_execution,
            'maintenance_in_execution': maintenance_in_execution,
        }

    def _get_procedure_compliance(self):
        """Get procedure compliance metrics based on ICS procedures"""
        tender_obj = self.env['ics.tender']
        project_obj = self.env['project.project']

        won_supply = tender_obj.search_count([
            ('state', '=', 'won'),
            ('tender_category', '=', 'supply')
        ])

        won_maintenance = tender_obj.search_count([
            ('state', '=', 'won'),
            ('tender_category', '=', 'maintenance')
        ])

        supply_with_projects = 0
        if won_supply > 0:
            supply_tenders = tender_obj.search([
                ('state', '=', 'won'),
                ('tender_category', '=', 'supply')
            ])
            supply_with_projects = project_obj.search_count([
                ('tender_id', 'in', supply_tenders.ids)
            ])

        maintenance_with_projects = 0
        if won_maintenance > 0:
            maintenance_tenders = tender_obj.search([
                ('state', '=', 'won'),
                ('tender_category', '=', 'maintenance')
            ])
            maintenance_with_projects = project_obj.search_count([
                ('tender_id', 'in', maintenance_tenders.ids)
            ])

        supply_compliance = (supply_with_projects / won_supply * 100) if won_supply > 0 else 100
        maintenance_compliance = (maintenance_with_projects / won_maintenance * 100) if won_maintenance > 0 else 100

        return {
            'supply_won': won_supply,
            'supply_with_projects': supply_with_projects,
            'supply_compliance': round(supply_compliance, 1),
            'maintenance_won': won_maintenance,
            'maintenance_with_projects': maintenance_with_projects,
            'maintenance_compliance': round(maintenance_compliance, 1),
            'overall_compliance': round((supply_compliance + maintenance_compliance) / 2, 1) if (won_supply > 0 or won_maintenance > 0) else 100,
        }

    def _get_win_loss_ratio(self):
        """Calculate win/loss ratio and success rate"""
        tender_obj = self.env['ics.tender']

        won_count = tender_obj.search_count([('state', '=', 'won')])
        lost_count = tender_obj.search_count([('state', '=', 'lost')])

        total_decided = won_count + lost_count
        win_rate = (won_count / total_decided * 100) if total_decided > 0 else 0
        loss_rate = (lost_count / total_decided * 100) if total_decided > 0 else 0

        return {
            'won_count': won_count,
            'lost_count': lost_count,
            'total_decided': total_decided,
            'win_rate': round(win_rate, 1),
            'loss_rate': round(loss_rate, 1),
        }
