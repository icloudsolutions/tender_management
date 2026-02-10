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
        domain="[('id', 'in', available_vendor_ids)]")
    
    available_vendor_ids = fields.Many2many('res.partner', 
        compute='_compute_available_vendors', 
        string='Available Vendors')

    @api.depends('tender_id', 'tender_id.boq_line_ids.vendor_offer_ids')
    def _compute_available_vendors(self):
        """Compute vendors who have submitted at least one offer"""
        for wizard in self:
            if wizard.tender_id:
                vendor_ids = wizard.tender_id.boq_line_ids.mapped('vendor_offer_ids.vendor_id').ids
                wizard.available_vendor_ids = [(6, 0, vendor_ids)]
            else:
                wizard.available_vendor_ids = [(5, 0, 0)]

    @api.depends('line_ids.best_offer_total')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_best_price = sum(wizard.line_ids.mapped('best_offer_total'))

    @api.model
    def default_get(self, fields_list):
        res = super(VendorComparisonWizard, self).default_get(fields_list)
        if self._context.get('default_tender_id'):
            tender = self.env['ics.tender'].browse(self._context['default_tender_id'])
            
            # Validate that BoQ lines exist
            if not tender.boq_line_ids:
                raise UserError(_('No BoQ lines found in this tender. Please add products first.'))
            
            # Check if any vendor offers exist
            total_offers = self.env['ics.tender.vendor.offer'].search_count([
                ('boq_line_id', 'in', tender.boq_line_ids.ids)
            ])
            
            if total_offers == 0:
                raise UserError(_(
                    'No supplier offers found!\n\n'
                    'To compare suppliers, follow these steps:\n'
                    '1. Click "Request Supplier Quotations" to send requests to potential suppliers\n'
                    '2. Enter each supplier\'s quoted prices in their quotation request\n'
                    '3. Click "Sync Supplier Prices" to import those prices\n'
                    '4. Then click "Compare Suppliers" to review and select the best offers'
                ))
            
            lines = []
            lines_without_offers = []
            
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
                else:
                    # Track lines without offers for warning
                    lines_without_offers.append(boq_line.name or boq_line.product_id.name)
            
            res['line_ids'] = lines
            
            # Show warning if some lines don't have offers
            if lines_without_offers:
                # Note: Can't raise UserError here as we want to show the wizard
                # The warning will be displayed in the view
                pass
                
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
        """Apply vendor selection for product-wise mode"""
        for line in self.line_ids:
            if line.best_vendor_id:
                # Get the actual offer for this vendor-product combination
                vendor_offer = self.env['ics.tender.vendor.offer'].search([
                    ('boq_line_id', '=', line.boq_line_id.id),
                    ('vendor_id', '=', line.best_vendor_id.id)
                ], limit=1)
                
                if vendor_offer:
                    line.boq_line_id.write({
                        'selected_vendor_id': line.best_vendor_id.id,
                        'selected_vendor_price': vendor_offer.total_price,
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

    best_vendor_id = fields.Many2one('res.partner', string='Best Vendor',
        help='Best vendor based on lowest price. You can change this selection manually.',
        domain="[('id', 'in', available_vendor_ids)]")
    
    available_vendor_ids = fields.Many2many('res.partner',
        compute='_compute_available_vendors_for_line',
        string='Available Vendors for this product')

    best_offer_unit_price = fields.Float('Best Unit Price', readonly=True)

    best_offer_total = fields.Monetary('Best Total Price', readonly=True,
        currency_field='currency_id')

    offer_count = fields.Integer('Number of Offers', readonly=True)

    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')

    savings = fields.Monetary('Savings', compute='_compute_savings',
        currency_field='currency_id')

    savings_percentage = fields.Float('Savings %', compute='_compute_savings')

    @api.depends('boq_line_id', 'boq_line_id.vendor_offer_ids')
    def _compute_available_vendors_for_line(self):
        """Compute vendors who have offers for this specific product"""
        for line in self:
            if line.boq_line_id:
                vendor_ids = line.boq_line_id.vendor_offer_ids.mapped('vendor_id').ids
                line.available_vendor_ids = [(6, 0, vendor_ids)]
            else:
                line.available_vendor_ids = [(5, 0, 0)]

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
    
    @api.onchange('best_vendor_id')
    def _onchange_best_vendor_id(self):
        """Update prices when vendor selection changes"""
        if self.best_vendor_id and self.boq_line_id:
            vendor_offer = self.env['ics.tender.vendor.offer'].search([
                ('boq_line_id', '=', self.boq_line_id.id),
                ('vendor_id', '=', self.best_vendor_id.id)
            ], limit=1)
            
            if vendor_offer:
                self.best_offer_unit_price = vendor_offer.unit_price
                self.best_offer_total = vendor_offer.total_price

    def action_view_offers(self):
        self.ensure_one()
        return {
            'name': _('Vendor Offers'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.vendor.offer',
            'view_mode': 'list,form',
            'domain': [('boq_line_id', '=', self.boq_line_id.id)],
            'target': 'new',
        }
