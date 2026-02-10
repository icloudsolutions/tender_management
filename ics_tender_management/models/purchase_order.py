from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        """Override to auto-sync vendor offers when PO is confirmed."""
        res = super().button_confirm()
        self._sync_vendor_offers_to_tender()
        return res

    def _sync_vendor_offers_to_tender(self):
        """Create/update vendor offers in linked tenders when PO is confirmed."""
        VendorOffer = self.env['ics.tender.vendor.offer']
        
        for po in self:
            # Find tender through purchase agreement (requisition)
            if not po.requisition_id or not po.requisition_id.tender_id:
                continue
            
            tender = po.requisition_id.tender_id
            vendor = po.partner_id
            if not vendor or not tender.boq_line_ids:
                continue
            
            for po_line in po.order_line:
                product = po_line.product_id
                if not product or po_line.price_unit <= 0:
                    continue
                
                # Find matching BoQ line
                boq_line = tender.boq_line_ids.filtered(
                    lambda l: l.product_id.id == product.id
                )
                if not boq_line:
                    continue
                boq_line = boq_line[0]
                
                # Check for existing offer
                existing_offer = VendorOffer.search([
                    ('boq_line_id', '=', boq_line.id),
                    ('vendor_id', '=', vendor.id),
                ], limit=1)
                
                if existing_offer:
                    if existing_offer.unit_price != po_line.price_unit:
                        existing_offer.write({
                            'unit_price': po_line.price_unit,
                            'purchase_order_id': po.id,
                        })
                else:
                    VendorOffer.create({
                        'boq_line_id': boq_line.id,
                        'vendor_id': vendor.id,
                        'unit_price': po_line.price_unit,
                        'purchase_order_id': po.id,
                    })
