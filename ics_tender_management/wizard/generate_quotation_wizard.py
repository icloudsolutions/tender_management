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
        string='Preview Lines', compute='_compute_preview_lines')

    total_cost = fields.Monetary('Total Cost', compute='_compute_totals',
        currency_field='currency_id')

    total_margin = fields.Monetary('Total Margin', compute='_compute_totals',
        currency_field='currency_id')

    total_amount = fields.Monetary('Total Amount', compute='_compute_totals',
        currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='tender_id.currency_id')

    @api.depends('tender_id.boq_line_ids', 'margin_percentage', 'use_vendor_costs')
    def _compute_preview_lines(self):
        for wizard in self:
            lines = []
            for boq_line in wizard.tender_id.boq_line_ids:
                if wizard.use_vendor_costs and boq_line.selected_vendor_price:
                    cost = boq_line.selected_vendor_price
                else:
                    cost = boq_line.estimated_cost

                margin = cost * (wizard.margin_percentage / 100)
                total = cost + margin

                lines.append((0, 0, {
                    'product_id': boq_line.product_id.id,
                    'name': boq_line.name,
                    'quantity': boq_line.quantity,
                    'uom_id': boq_line.uom_id.id,
                    'cost': cost,
                    'margin': margin,
                    'unit_price': total / boq_line.quantity if boq_line.quantity else 0,
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

        quotation_vals = {
            'partner_id': self.partner_id.id,
            'tender_id': self.tender_id.id,
            'validity_date': self.validity_date,
            'payment_term_id': self.payment_term_id.id if self.payment_term_id else False,
            'pricelist_id': self.pricelist_id.id if self.pricelist_id else False,
            'note': self.notes,
            'user_id': self.tender_id.user_id.id,
            'team_id': self.tender_id.team_id.id if self.tender_id.team_id else False,
        }

        quotation = self.env['sale.order'].create(quotation_vals)

        for preview_line in self.line_preview_ids:
            self.env['sale.order.line'].create({
                'order_id': quotation.id,
                'product_id': preview_line.product_id.id,
                'name': preview_line.name,
                'product_uom_qty': preview_line.quantity,
                'product_uom': preview_line.uom_id.id,
                'price_unit': preview_line.unit_price,
            })

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
