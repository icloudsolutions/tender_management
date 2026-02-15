from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GenerateQuotationWizard(models.TransientModel):
    _name = 'ics.tender.quotation.wizard'
    _description = 'Generate Quotation Wizard'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)

    partner_id = fields.Many2one('res.partner', string='Customer',
        related='tender_id.partner_id', readonly=True)

    margin_percentage = fields.Float('Margin %', required=True, default=20.0)

    use_vendor_costs = fields.Boolean('Use Selected Vendor Costs', default=True,
        help='If checked, uses selected vendor prices. Otherwise uses estimated costs.')

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')

    validity_date = fields.Date('Quotation Validity',
        default=lambda self: fields.Date.today())

    notes = fields.Html('Terms and Conditions')

    line_preview_ids = fields.One2many('ics.tender.quotation.line.preview', 'wizard_id',
        string='Preview Lines', compute='_compute_preview_lines', store=False, readonly=True)

    total_cost = fields.Monetary('Total Cost', compute='_compute_totals',
        currency_field='currency_id')

    total_margin = fields.Monetary('Total Margin', compute='_compute_totals',
        currency_field='currency_id')

    total_amount = fields.Monetary('Total Amount', compute='_compute_totals',
        currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='tender_id.currency_id')

    @api.depends(
        'tender_id.boq_line_ids',
        'tender_id.boq_line_ids.quantity',
        'tender_id.boq_line_ids.estimated_cost',
        'tender_id.boq_line_ids.selected_vendor_price',
        'tender_id.boq_line_ids.selected_vendor_id',
        'margin_percentage',
        'use_vendor_costs',
    )
    def _compute_preview_lines(self):
        """Build preview from BoQ: cost per line = (unit cost × qty), margin on line total, total = cost + margin."""
        for wizard in self:
            lines = []
            for boq_line in wizard.tender_id.boq_line_ids:
                # Line cost = total for line (already unit × qty from BoQ)
                if wizard.use_vendor_costs and boq_line.selected_vendor_id:
                    cost = boq_line.selected_vendor_price or 0.0
                else:
                    cost = boq_line.estimated_cost or 0.0

                # Margin and line total (all quantity-based)
                margin = cost * (wizard.margin_percentage / 100)
                total = cost + margin

                # Sale unit price = line total / qty so that qty × unit_price = total
                qty = boq_line.quantity or 0.0
                if qty > 0:
                    unit_price = total / qty
                else:
                    unit_price = total

                lines.append((0, 0, {
                    'product_id': boq_line.product_id.id,
                    'name': boq_line.name or (boq_line.product_id.name if boq_line.product_id else 'Product'),
                    'quantity': qty,
                    'uom_id': boq_line.uom_id.id,
                    'cost': cost,
                    'margin': margin,
                    'unit_price': unit_price,
                    'total': total,
                }))

            wizard.line_preview_ids = lines

    @api.depends('line_preview_ids.cost', 'line_preview_ids.margin', 'line_preview_ids.total')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_cost = sum(wizard.line_preview_ids.mapped('cost'))
            wizard.total_margin = sum(wizard.line_preview_ids.mapped('margin'))
            wizard.total_amount = sum(wizard.line_preview_ids.mapped('total'))

    def action_generate_quotation(self):
        self.ensure_one()

        if not self.tender_id.boq_line_ids:
            raise UserError(_('No BoQ lines found in the tender.'))

        if not self.partner_id:
            raise UserError(_('Please set a customer on the tender before generating quotation.'))
        
        if self.margin_percentage < 0:
            raise UserError(_('Margin percentage cannot be negative.'))

        # Check if we're updating an existing quotation
        regenerate_id = self._context.get('regenerate_quotation_id')
        if regenerate_id:
            return self._update_existing_quotation(regenerate_id)

        return self._create_new_quotation()

    def _create_new_quotation(self):
        """Create a new sales quotation from the tender BoQ."""
        # Build quotation vals with only available fields
        so_model = self.env['sale.order']
        so_fields = so_model._fields.keys()
        
        quotation_vals = {
            'partner_id': self.partner_id.id,
        }
        
        # Add optional fields if they exist
        if 'tender_id' in so_fields:
            quotation_vals['tender_id'] = self.tender_id.id
        if 'validity_date' in so_fields:
            quotation_vals['validity_date'] = self.validity_date
        if 'payment_term_id' in so_fields and self.payment_term_id:
            quotation_vals['payment_term_id'] = self.payment_term_id.id
        if 'pricelist_id' in so_fields and self.pricelist_id:
            quotation_vals['pricelist_id'] = self.pricelist_id.id
        if 'note' in so_fields and self.notes:
            quotation_vals['note'] = self.notes
        if 'user_id' in so_fields and self.tender_id.user_id:
            quotation_vals['user_id'] = self.tender_id.user_id.id
        if 'team_id' in so_fields and self.tender_id.team_id:
            quotation_vals['team_id'] = self.tender_id.team_id.id

        quotation = so_model.create(quotation_vals)
        self._create_quotation_lines(quotation)

        self.tender_id.write({
            'state': 'quotation',
            'margin_percentage': self.margin_percentage,
        })

        return {
            'name': _('Sales Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': quotation.id,
            'target': 'current',
        }

    def _update_existing_quotation(self, quotation_id):
        """Update an existing quotation: remove old lines, recreate from current BoQ."""
        quotation = self.env['sale.order'].browse(quotation_id)
        if not quotation.exists():
            return self._create_new_quotation()

        so_fields = quotation._fields.keys()

        # Update header fields
        update_vals = {}
        if 'validity_date' in so_fields:
            update_vals['validity_date'] = self.validity_date
        if 'payment_term_id' in so_fields and self.payment_term_id:
            update_vals['payment_term_id'] = self.payment_term_id.id
        if 'pricelist_id' in so_fields and self.pricelist_id:
            update_vals['pricelist_id'] = self.pricelist_id.id
        if 'note' in so_fields and self.notes:
            update_vals['note'] = self.notes
        if update_vals:
            quotation.write(update_vals)

        # Remove existing lines and recreate
        quotation.order_line.unlink()
        self._create_quotation_lines(quotation)

        self.tender_id.write({
            'margin_percentage': self.margin_percentage,
        })

        return {
            'name': _('Sales Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': quotation.id,
            'target': 'current',
        }

    def _create_quotation_lines(self, quotation):
        """Create sale order lines from preview lines."""
        sol_model = self.env['sale.order.line']
        sol_fields = sol_model._fields.keys()

        for preview_line in self.line_preview_ids:
            sol_vals = {
                'order_id': quotation.id,
            }
            
            if 'product_id' in sol_fields and preview_line.product_id:
                sol_vals['product_id'] = preview_line.product_id.id
            if 'name' in sol_fields and preview_line.name:
                sol_vals['name'] = preview_line.name
            if 'product_uom_qty' in sol_fields:
                sol_vals['product_uom_qty'] = preview_line.quantity
            if 'product_uom' in sol_fields and preview_line.uom_id:
                sol_vals['product_uom'] = preview_line.uom_id.id
            if 'price_unit' in sol_fields:
                sol_vals['price_unit'] = preview_line.unit_price
                
            sol_model.create(sol_vals)


class QuotationLinePreview(models.TransientModel):
    _name = 'ics.tender.quotation.line.preview'
    _description = 'Quotation Line Preview'

    wizard_id = fields.Many2one('ics.tender.quotation.wizard',
        string='Wizard', required=True, ondelete='cascade')

    product_id = fields.Many2one('product.product', string='Product', readonly=True)

    name = fields.Char('Description', readonly=True)

    quantity = fields.Float('Quantity', readonly=True)

    uom_id = fields.Many2one('uom.uom', string='UoM', readonly=True)

    cost = fields.Monetary('Cost', readonly=True, currency_field='currency_id')

    margin = fields.Monetary('Margin', readonly=True, currency_field='currency_id')

    unit_price = fields.Float('Unit Price', readonly=True)

    total = fields.Monetary('Total', readonly=True, currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')
