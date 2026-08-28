# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SmbDashboard(models.Model):
    _name = 'smb.dashboard'
    _description = 'SMB Dashboard'

    name = fields.Char(string='Dashboard', default='SMB Dashboard')

    @api.model
    def get_smb_statistics(self):
        """Statistics for SMB dashboard: credit, orders, collection, projects."""
        SaleOrder = self.env['sale.order']
        today = fields.Date.context_today(self)

        # Credit workflow
        pending_credit = SaleOrder.search_count([
            ('smb_credit_state', '=', 'sent_to_credit'),
            ('state', 'in', ('draft', 'sent')),
        ])
        credit_approved = SaleOrder.search_count([
            ('smb_credit_state', '=', 'credit_approved'),
        ])
        credit_rejected = SaleOrder.search_count([
            ('smb_credit_state', '=', 'credit_rejected'),
        ])
        total_quotations = SaleOrder.search_count([
            ('state', 'in', ('draft', 'sent')),
        ])
        confirmed_orders = SaleOrder.search_count([
            ('state', 'in', ('sale', 'done')),
        ])

        # Overdue invoices (collection)
        overdue_invoices = 0
        if 'account.move' in self.env:
            overdue_invoices = self.env['account.move'].search_count([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('invoice_date_due', '<', today),
            ])

        # Delivery projects (projects linked to SO)
        delivery_projects = 0
        if 'project.project' in self.env:
            delivery_projects = self.env['project.project'].search_count([
                ('sale_order_id', '!=', False),
            ])

        # Credit state distribution (for chart)
        credit_distribution = self._get_credit_state_distribution(SaleOrder)
        # Monthly trend: orders confirmed last 6 months
        monthly_trend = self._get_monthly_trend(SaleOrder)

        return {
            'pending_credit': pending_credit,
            'credit_approved': credit_approved,
            'credit_rejected': credit_rejected,
            'total_quotations': total_quotations,
            'confirmed_orders': confirmed_orders,
            'overdue_invoices': overdue_invoices,
            'delivery_projects': delivery_projects,
            'credit_distribution': credit_distribution,
            'monthly_trend': monthly_trend,
        }

    def _get_credit_state_distribution(self, sale_order_obj):
        labels = []
        values = []
        for state, label in [
            ('sent_to_credit', 'Pending Credit'),
            ('credit_approved', 'Credit Approved'),
            ('credit_rejected', 'Credit Rejected'),
        ]:
            count = sale_order_obj.search_count([('smb_credit_state', '=', state)])
            if count > 0:
                labels.append(label)
                values.append(count)
        return {'labels': labels, 'values': values}

    def _get_monthly_trend(self, sale_order_obj):
        months = []
        values = []
        today = datetime.today()
        for i in range(5, -1, -1):
            month_start = (today - relativedelta(months=i)).replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            count = sale_order_obj.search_count([
                ('state', 'in', ('sale', 'done')),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d')),
                ('date_order', '<=', month_end.strftime('%Y-%m-%d')),
            ])
            months.append(month_start.strftime('%b'))
            values.append(count)
        return {'labels': months, 'values': values}
