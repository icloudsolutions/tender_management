from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TenderBoQLine(models.Model):
    _name = 'ics.tender.boq.line'
    _description = 'Tender Bill of Quantities Line'
    _order = 'sequence, id'

    tender_id = fields.Many2one('ics.tender', string='Tender',
        required=True, ondelete='cascade')

    tender_type = fields.Selection(related='tender_id.tender_type', string='Tender Type', store=True, readonly=True)

    sequence = fields.Integer('Sequence', default=10)

    name = fields.Char('Description', required=True)

    product_id = fields.Many2one('product.product', string='Product',
        domain=[('purchase_ok', '=', True)])

    product_category_id = fields.Many2one('product.category', string='Category')

    quantity = fields.Float('Quantity', required=True, default=1.0)

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)

    estimated_cost = fields.Monetary('Estimated Cost',
        currency_field='currency_id',
        help='Your initial estimated cost for this line')

    currency_id = fields.Many2one('res.currency', string='Currency',
        related='tender_id.currency_id', readonly=True)

    unit_price = fields.Float('Unit Price', compute='_compute_unit_price', store=True)

    vendor_offer_ids = fields.One2many('ics.tender.vendor.offer', 'boq_line_id',
        string='Vendor Offers')

    selected_vendor_id = fields.Many2one('res.partner', string='Selected Vendor',
        domain=[('is_company', '=', True)])

    selected_vendor_price = fields.Monetary('Selected Vendor Price',
        currency_field='currency_id',
        compute='_compute_selected_vendor_price', store=True,
        help='Total from selected vendor offer (unit price × quantity).')

    notes = fields.Text('Notes')

    specifications = fields.Html('Technical Specifications')

    offer_count = fields.Integer('Number of Offers', compute='_compute_offer_count')

    @api.depends('vendor_offer_ids')
    def _compute_offer_count(self):
        for line in self:
            line.offer_count = len(line.vendor_offer_ids)

    @api.depends('vendor_offer_ids', 'vendor_offer_ids.total_price', 'selected_vendor_id', 'quantity')
    def _compute_selected_vendor_price(self):
        """Total from selected vendor offer (unit price × quantity), so totals stay qty-based."""
        for line in self:
            offer = line.vendor_offer_ids.filtered(lambda o: o.vendor_id == line.selected_vendor_id)[:1]
            line.selected_vendor_price = offer.total_price if offer else 0.0

    @api.depends('estimated_cost', 'quantity')
    def _compute_unit_price(self):
        for line in self:
            if line.quantity:
                line.unit_price = line.estimated_cost / line.quantity
            else:
                line.unit_price = 0.0

    @api.onchange('quantity')
    def _onchange_quantity_estimated_cost(self):
        """Keep line total quantity-based: estimated_cost = unit_price * quantity."""
        if self.quantity and self.unit_price is not None:
            self.estimated_cost = self.unit_price * self.quantity

    def write(self, vals):
        """When quantity changes, recompute estimated_cost = unit_price * quantity so totals stay qty-based."""
        if self.env.context.get('skip_quantity_update'):
            return super().write(vals)
        if 'quantity' in vals and 'estimated_cost' not in vals:
            old_unit_prices = {l.id: l.unit_price for l in self}
        else:
            old_unit_prices = {}
        res = super().write(vals)
        if old_unit_prices:
            for line in self:
                new_total = old_unit_prices[line.id] * line.quantity
                super(TenderBoQLine, line).with_context(skip_quantity_update=True).write({'estimated_cost': new_total})
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.uom_id = self.product_id.uom_po_id
            self.product_category_id = self.product_id.categ_id
            if self.product_id.standard_price and self.quantity:
                self.estimated_cost = self.product_id.standard_price * self.quantity

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))


class TenderVendorOffer(models.Model):
    _name = 'ics.tender.vendor.offer'
    _description = 'Tender Vendor Offer'
    _order = 'unit_price'

    boq_line_id = fields.Many2one('ics.tender.boq.line', string='BoQ Line',
        required=True, ondelete='cascade')

    tender_id = fields.Many2one('ics.tender', string='Tender',
        related='boq_line_id.tender_id', store=True)

    vendor_id = fields.Many2one('res.partner', string='Vendor',
        required=True, domain=[('is_company', '=', True)])

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')

    unit_price = fields.Float('Unit Price', required=True)

    quantity = fields.Float('Quantity', related='boq_line_id.quantity')

    total_price = fields.Float('Total Price', compute='_compute_total_price', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
        related='tender_id.currency_id', readonly=True)

    delivery_lead_time = fields.Integer('Delivery Lead Time (Days)')

    payment_terms = fields.Char('Payment Terms')

    notes = fields.Text('Notes')

    is_selected = fields.Boolean('Selected',
        compute='_compute_is_selected')

    @api.depends('unit_price', 'quantity')
    def _compute_total_price(self):
        for offer in self:
            offer.total_price = offer.unit_price * offer.quantity

    @api.depends('boq_line_id.selected_vendor_id')
    def _compute_is_selected(self):
        for offer in self:
            offer.is_selected = offer.vendor_id == offer.boq_line_id.selected_vendor_id

    def action_select_vendor(self):
        self.ensure_one()
        self.boq_line_id.write({'selected_vendor_id': self.vendor_id.id})
