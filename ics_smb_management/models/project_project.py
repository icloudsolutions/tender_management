# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Ensure sale_order_id exists for SMB delivery projects (ics_tender_management also adds it)
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        ondelete='set null',
        help='Linked Sale Order for delivery/logistics tracking (SMB).',
    )

    def action_view_sale_order(self):
        self.ensure_one()
        if not self.sale_order_id:
            return {}
        return {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
