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
        project creation fails with ValueError. We fix this in two ways:
        1. Try to recreate the folder and clear the ORM cache
        2. If that fails, disable use_documents to prevent the crash
        """
        if self._is_document_folder_missing():
            fixed = self._fix_document_project_folder()
            if not fixed:
                # Fallback: disable use_documents to prevent crash
                _logger.warning(
                    "Could not fix missing documents_project folder. "
                    "Disabling use_documents for new projects."
                )
                if isinstance(vals_list, dict):
                    vals_list['use_documents'] = False
                else:
                    for vals in vals_list:
                        vals['use_documents'] = False
        return super().create(vals_list)

    @api.model
    def _is_document_folder_missing(self):
        """Check if documents_project folder XML ID is missing."""
        if 'documents.folder' not in self.env:
            return False
        imd = self.env['ir.model.data'].sudo().search([
            ('module', '=', 'documents_project'),
            ('name', '=', 'document_project_folder'),
        ], limit=1)
        if not imd:
            return True
        # Also check if the actual folder record still exists
        if not self.env['documents.folder'].sudo().browse(imd.res_id).exists():
            # XML ID exists but points to deleted folder - remove stale reference
            imd.unlink()
            return True
        return False

    @api.model
    def _fix_document_project_folder(self):
        """Recreate the missing documents_project folder and clear ORM cache."""
        try:
            _logger.warning(
                "Missing 'documents_project.document_project_folder'. "
                "Attempting to recreate..."
            )
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
            # Flush writes to database so env.ref() can find them
            self.env.flush_all()
            # Clear ORM cache so env.ref() doesn't return stale "not found"
            self.env.registry.clear_cache()
            
            _logger.info(
                "Successfully recreated 'documents_project.document_project_folder' "
                "(folder ID: %s)", folder.id
            )
            return True
        except Exception as e:
            _logger.error(
                "Failed to recreate documents_project folder: %s", e
            )
            return False

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
