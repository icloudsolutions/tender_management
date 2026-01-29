from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    tender_id = fields.Many2one('ics.tender', string='Related Tender',
        ondelete='restrict', tracking=True)

    sale_order_id = fields.Many2one('sale.order', string='Sales Order')

    def action_view_tender(self):
        self.ensure_one()
        if not self.tender_id:
            return {}
        return {
            'name': 'Tender',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender',
            'view_mode': 'form',
            'res_id': self.tender_id.id,
            'target': 'current',
        }

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
