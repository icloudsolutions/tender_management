from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tender_id = fields.Many2one('ics.tender', string='Related Tender', ondelete='restrict')
    is_tender_rfq = fields.Boolean(
        'Tender RFQ', default=False,
        help='If True, this is a pre-win Request for Quotation to collect supplier prices. '
             'If False, this is a post-win Purchase Order for project execution.')

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
