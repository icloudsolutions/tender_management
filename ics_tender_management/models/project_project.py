import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    tender_id = fields.Many2one('ics.tender', string='Related Tender',
        ondelete='restrict', tracking=True)

    sale_order_id = fields.Many2one('sale.order', string='Sales Order')

    @api.model_create_multi
    def create(self, vals_list):
        """Override to fix missing documents_project folder before project creation.
        
        The documents_project enterprise module expects the XML record
        'documents_project.document_project_folder' to exist. If it was deleted,
        project creation fails with ValueError. This recreates it if missing.
        """
        self._ensure_document_project_folder()
        return super().create(vals_list)

    @api.model
    def _ensure_document_project_folder(self):
        """Recreate the documents_project folder if it was deleted."""
        if 'documents.folder' not in self.env:
            return  # documents module not installed
        try:
            self.env.ref('documents_project.document_project_folder')
        except ValueError:
            _logger.warning(
                "Missing XML record 'documents_project.document_project_folder'. "
                "Recreating the folder to fix project creation."
            )
            try:
                folder = self.env['documents.folder'].sudo().create({
                    'name': 'Projects',
                })
                self.env['ir.model.data'].sudo().create({
                    'name': 'document_project_folder',
                    'module': 'documents_project',
                    'model': 'documents.folder',
                    'res_id': folder.id,
                    'noupdate': True,
                })
                _logger.info(
                    "Successfully recreated 'documents_project.document_project_folder' "
                    "(folder ID: %s)", folder.id
                )
            except Exception as e:
                _logger.error(
                    "Failed to recreate documents_project folder: %s. "
                    "You may need to reinstall the documents_project module.", e
                )

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
