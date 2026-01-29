from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VendorComparisonWizard(models.TransientModel):
    _name = 'ics.tender.vendor.comparison.wizard'
    _description = 'Vendor Comparison Wizard'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True)

    line_ids = fields.One2many('ics.tender.vendor.comparison.line', 'wizard_id',
        string='Comparison Lines')

    total_best_price = fields.Monetary('Total Best Price',
        compute='_compute_totals', currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='tender_id.currency_id')

    @api.depends('line_ids.best_offer_total')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_best_price = sum(wizard.line_ids.mapped('best_offer_total'))

    @api.model
    def default_get(self, fields_list):
        res = super(VendorComparisonWizard, self).default_get(fields_list)
        if self._context.get('default_tender_id'):
            tender = self.env['ics.tender'].browse(self._context['default_tender_id'])
            lines = []
            for boq_line in tender.boq_line_ids:
                vendor_offers = self.env['ics.tender.vendor.offer'].search([
                    ('boq_line_id', '=', boq_line.id)
                ], order='unit_price')

                if vendor_offers:
                    best_offer = vendor_offers[0]
                    lines.append((0, 0, {
                        'boq_line_id': boq_line.id,
                        'product_id': boq_line.product_id.id,
                        'quantity': boq_line.quantity,
                        'uom_id': boq_line.uom_id.id,
                        'estimated_cost': boq_line.estimated_cost,
                        'best_vendor_id': best_offer.vendor_id.id,
                        'best_offer_unit_price': best_offer.unit_price,
                        'best_offer_total': best_offer.total_price,
                        'offer_count': len(vendor_offers),
                    }))
            res['line_ids'] = lines
        return res

    def action_apply_selection(self):
        self.ensure_one()
        for line in self.line_ids:
            if line.best_vendor_id:
                line.boq_line_id.write({
                    'selected_vendor_id': line.best_vendor_id.id,
                    'selected_vendor_price': line.best_offer_total,
                })
        return {'type': 'ir.actions.act_window_close'}


class VendorComparisonLine(models.TransientModel):
    _name = 'ics.tender.vendor.comparison.line'
    _description = 'Vendor Comparison Line'

    wizard_id = fields.Many2one('ics.tender.vendor.comparison.wizard',
        string='Wizard', required=True, ondelete='cascade')

    boq_line_id = fields.Many2one('ics.tender.boq.line', string='BoQ Line', required=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)

    quantity = fields.Float('Quantity', readonly=True)

    uom_id = fields.Many2one('uom.uom', string='UoM', readonly=True)

    estimated_cost = fields.Monetary('Estimated Cost', readonly=True,
        currency_field='currency_id')

    best_vendor_id = fields.Many2one('res.partner', string='Best Vendor', readonly=True)

    best_offer_unit_price = fields.Float('Best Unit Price', readonly=True)

    best_offer_total = fields.Monetary('Best Total Price', readonly=True,
        currency_field='currency_id')

    offer_count = fields.Integer('Number of Offers', readonly=True)

    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')

    savings = fields.Monetary('Savings', compute='_compute_savings',
        currency_field='currency_id')

    savings_percentage = fields.Float('Savings %', compute='_compute_savings')

    @api.depends('estimated_cost', 'best_offer_total')
    def _compute_savings(self):
        for line in self:
            if line.estimated_cost and line.best_offer_total:
                line.savings = line.estimated_cost - line.best_offer_total
                if line.estimated_cost > 0:
                    line.savings_percentage = (line.savings / line.estimated_cost) * 100
                else:
                    line.savings_percentage = 0.0
            else:
                line.savings = 0.0
                line.savings_percentage = 0.0

    def action_view_offers(self):
        self.ensure_one()
        return {
            'name': _('Vendor Offers'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.vendor.offer',
            'view_mode': 'tree,form',
            'domain': [('boq_line_id', '=', self.boq_line_id.id)],
            'target': 'new',
        }
