from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VendorComparisonWizard(models.TransientModel):
    _name = 'ics.tender.vendor.comparison.wizard'
    _description = 'Vendor Comparison Wizard'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True)

    tender_type = fields.Selection(related='tender_id.tender_type', string='Tender Type', readonly=True)

    line_ids = fields.One2many('ics.tender.vendor.comparison.line', 'wizard_id',
        string='Comparison Lines')

    total_best_price = fields.Monetary('Total Best Price',
        compute='_compute_totals', currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='tender_id.currency_id')

    single_vendor_id = fields.Many2one('res.partner', string='Selected Vendor',
        help='For Single Vendor mode: This vendor will be applied to all products',
        domain=[('is_company', '=', True)])

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

        if self.tender_type == 'single_vendor':
            return self._apply_single_vendor_selection()
        else:
            return self._apply_product_wise_selection()

    def _apply_single_vendor_selection(self):
        if not self.single_vendor_id:
            raise UserError(_('Please select a vendor for Single Vendor mode.'))

        for line in self.line_ids:
            vendor_offer = self.env['ics.tender.vendor.offer'].search([
                ('boq_line_id', '=', line.boq_line_id.id),
                ('vendor_id', '=', self.single_vendor_id.id)
            ], limit=1)

            if not vendor_offer:
                raise UserError(_(
                    'Vendor %s has no offer for product: %s\n'
                    'Please ensure the selected vendor has submitted offers for all products.'
                ) % (self.single_vendor_id.name, line.product_id.name or line.boq_line_id.name))

            line.boq_line_id.write({
                'selected_vendor_id': self.single_vendor_id.id,
                'selected_vendor_price': vendor_offer.total_price,
            })

        return {'type': 'ir.actions.act_window_close'}

    def _apply_product_wise_selection(self):
        for line in self.line_ids:
            if line.best_vendor_id:
                line.boq_line_id.write({
                    'selected_vendor_id': line.best_vendor_id.id,
                    'selected_vendor_price': line.best_offer_total,
                })

        return {'type': 'ir.actions.act_window_close'}

    def action_select_best_common_vendor(self):
        self.ensure_one()

        if self.tender_type != 'single_vendor':
            raise UserError(_('This action is only for Single Vendor mode.'))

        boq_lines = self.tender_id.boq_line_ids
        if not boq_lines:
            raise UserError(_('No BoQ lines found.'))

        all_vendors = self.env['res.partner']
        for boq_line in boq_lines:
            line_vendors = boq_line.vendor_offer_ids.mapped('vendor_id')
            if not all_vendors:
                all_vendors = line_vendors
            else:
                all_vendors &= line_vendors

        if not all_vendors:
            raise UserError(_(
                'No common vendor found with offers for all products.\n'
                'Please ensure at least one vendor has submitted offers for all items.'
            ))

        vendor_totals = {}
        for vendor in all_vendors:
            total = 0
            for boq_line in boq_lines:
                offer = self.env['ics.tender.vendor.offer'].search([
                    ('boq_line_id', '=', boq_line.id),
                    ('vendor_id', '=', vendor.id)
                ], limit=1)
                if offer:
                    total += offer.total_price
            vendor_totals[vendor.id] = total

        best_vendor_id = min(vendor_totals, key=vendor_totals.get)
        self.single_vendor_id = best_vendor_id

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Best Vendor Selected'),
                'message': _('Selected: %s (Total: %s)') % (
                    self.single_vendor_id.name,
                    '{:,.2f}'.format(vendor_totals[best_vendor_id])
                ),
                'type': 'success',
                'sticky': False,
            }
        }


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
