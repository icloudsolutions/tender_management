from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import io
import xlrd
import logging

_logger = logging.getLogger(__name__)


class ImportBoQWizard(models.TransientModel):
    _name = 'ics.tender.import.boq.wizard'
    _description = 'Import BoQ from Excel'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)

    file = fields.Binary('Excel File', required=True,
        help='Upload Excel file with columns: Product Code, Description, Quantity, UoM, Estimated Cost')

    filename = fields.Char('Filename')

    import_option = fields.Selection([
        ('replace', 'Replace Existing Lines'),
        ('append', 'Append to Existing Lines'),
    ], string='Import Option', default='append', required=True)

    def action_import_boq(self):
        """Import BoQ lines from Excel file"""
        self.ensure_one()

        if not self.file:
            raise UserError(_('Please upload an Excel file'))

        try:
            # Decode file
            file_data = base64.b64decode(self.file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)

            # Validate headers
            if sheet.nrows < 2:
                raise UserError(_('Excel file must contain headers and at least one data row'))

            # Expected headers: Product Code, Description, Quantity, UoM, Estimated Cost
            # Row 0 is headers, data starts from row 1

            # Clear existing lines if replace option
            if self.import_option == 'replace':
                self.tender_id.boq_line_ids.unlink()

            imported_count = 0
            errors = []

            for row_idx in range(1, sheet.nrows):
                try:
                    # Get values from cells
                    product_code = sheet.cell_value(row_idx, 0) if sheet.ncols > 0 else ''
                    description = sheet.cell_value(row_idx, 1) if sheet.ncols > 1 else ''
                    quantity = float(sheet.cell_value(row_idx, 2)) if sheet.ncols > 2 else 1.0
                    uom_name = sheet.cell_value(row_idx, 3) if sheet.ncols > 3 else ''
                    estimated_cost = float(sheet.cell_value(row_idx, 4)) if sheet.ncols > 4 else 0.0
                    specifications = sheet.cell_value(row_idx, 5) if sheet.ncols > 5 else ''

                    # Skip empty rows
                    if not description and not product_code:
                        continue

                    # Find product by code
                    product_id = False
                    if product_code:
                        product = self.env['product.product'].search([
                            '|',
                            ('default_code', '=', product_code),
                            ('barcode', '=', product_code)
                        ], limit=1)
                        if product:
                            product_id = product.id
                            if not description:
                                description = product.name

                    # Find UoM
                    uom_id = False
                    if uom_name:
                        uom = self.env['uom.uom'].search([
                            ('name', 'ilike', uom_name)
                        ], limit=1)
                        if uom:
                            uom_id = uom.id

                    # If no UoM found, use default Unit
                    if not uom_id:
                        uom_id = self.env.ref('uom.product_uom_unit').id

                    # Create BoQ line
                    self.env['ics.tender.boq.line'].create({
                        'tender_id': self.tender_id.id,
                        'product_id': product_id,
                        'name': description or 'Imported Item',
                        'quantity': quantity,
                        'uom_id': uom_id,
                        'estimated_cost': estimated_cost,
                        'specifications': f'<p>{specifications}</p>' if specifications else False,
                        'sequence': (row_idx - 1) * 10,
                    })

                    imported_count += 1

                except Exception as e:
                    errors.append(f'Row {row_idx + 1}: {str(e)}')
                    _logger.warning(f'Error importing row {row_idx + 1}: {str(e)}')

            # Show result
            if errors:
                error_msg = '\n'.join(errors)
                raise UserError(_(
                    'Import completed with errors:\n'
                    'Imported: %s lines\n'
                    'Errors:\n%s'
                ) % (imported_count, error_msg))
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('%s BoQ lines imported successfully') % imported_count,
                        'type': 'success',
                        'sticky': False,
                    }
                }

        except xlrd.XLRDError:
            raise UserError(_('Invalid Excel file. Please upload a valid .xls or .xlsx file'))
        except Exception as e:
            raise UserError(_('Error importing file: %s') % str(e))


class ExportBoQWizard(models.TransientModel):
    _name = 'ics.tender.export.boq.wizard'
    _description = 'Export BoQ to Excel'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)

    include_vendor_offers = fields.Boolean('Include Vendor Offers', default=False,
        help='Include vendor offers in separate columns')

    include_specifications = fields.Boolean('Include Technical Specifications', default=True)

    def action_export_boq(self):
        """Export BoQ lines to Excel file"""
        self.ensure_one()

        try:
            import xlwt
        except ImportError:
            raise UserError(_('Python xlwt library is required for Excel export. Please install it.'))

        # Create workbook
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('BoQ')

        # Styles
        header_style = xlwt.easyxf('font: bold on; align: horiz center')
        currency_style = xlwt.easyxf(num_format_str='#,##0.00')

        # Write headers
        headers = [
            'Product Code',
            'Description',
            'Quantity',
            'UoM',
            'Estimated Cost',
        ]

        if self.include_specifications:
            headers.append('Technical Specifications')

        if self.include_vendor_offers:
            headers.extend([
                'Selected Vendor',
                'Selected Vendor Price',
                'Number of Offers'
            ])

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_style)

        # Write data
        row_idx = 1
        for line in self.tender_id.boq_line_ids:
            sheet.write(row_idx, 0, line.product_id.default_code or '')
            sheet.write(row_idx, 1, line.name or '')
            sheet.write(row_idx, 2, line.quantity)
            sheet.write(row_idx, 3, line.uom_id.name or '')
            sheet.write(row_idx, 4, line.estimated_cost, currency_style)

            col_offset = 5

            if self.include_specifications:
                # Remove HTML tags from specifications
                import re
                specs = re.sub('<[^<]+?>', '', line.specifications or '')
                sheet.write(row_idx, col_offset, specs)
                col_offset += 1

            if self.include_vendor_offers:
                sheet.write(row_idx, col_offset, line.selected_vendor_id.name or '')
                sheet.write(row_idx, col_offset + 1, line.selected_vendor_price, currency_style)
                sheet.write(row_idx, col_offset + 2, line.offer_count)

            row_idx += 1

        # Save to BytesIO
        file_data = io.BytesIO()
        workbook.save(file_data)
        file_data.seek(0)

        # Create attachment
        filename = f'BOQ_{self.tender_id.name}.xls'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data.read()),
            'res_model': 'ics.tender',
            'res_id': self.tender_id.id,
            'mimetype': 'application/vnd.ms-excel',
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
