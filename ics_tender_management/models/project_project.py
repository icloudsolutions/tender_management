import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    tender_id = fields.Many2one('ics.tender', string='Related Tender',
        ondelete='restrict', tracking=True)

    sale_order_id = fields.Many2one('sale.order', string='Sales Order')

    def _create_missing_folders(self):
        """Override to handle missing documents_project folder gracefully.
        
        The documents_project enterprise module's _create_missing_folders() calls
        self.env.ref('documents_project.document_project_folder') which crashes
        with ValueError if that XML record was deleted from the database.
        
        This override catches that specific error, recreates the folder,
        and retries. If recreation fails, it skips folder creation silently.
        """
        try:
            return super()._create_missing_folders()
        except ValueError as e:
            if 'documents_project.document_project_folder' not in str(e):
                raise  # Re-raise if it's a different ValueError
            
            _logger.warning(
                "Missing 'documents_project.document_project_folder' record. "
                "Attempting to recreate and retry..."
            )
            
            # Try to recreate the folder
            try:
                if 'documents.folder' in self.env:
                    folder = self.env['documents.folder'].sudo().create({
                        'name': 'Projects',
                    })
                    # Remove any stale ir.model.data entry first
                    self.env['ir.model.data'].sudo().search([
                        ('module', '=', 'documents_project'),
                        ('name', '=', 'document_project_folder'),
                    ]).unlink()
                    # Create fresh XML ID
                    self.env['ir.model.data'].sudo().create({
                        'name': 'document_project_folder',
                        'module': 'documents_project',
                        'model': 'documents.folder',
                        'res_id': folder.id,
                        'noupdate': True,
                    })
                    self.env.flush_all()
                    self.env.registry.clear_cache()
                    
                    _logger.info(
                        "Recreated 'documents_project.document_project_folder' "
                        "(folder ID: %s). Retrying folder creation...", folder.id
                    )
                    # Retry the original method
                    try:
                        return super()._create_missing_folders()
                    except Exception:
                        _logger.warning(
                            "Retry of _create_missing_folders still failed. "
                            "Skipping document folder creation for projects."
                        )
            except Exception as create_err:
                _logger.error(
                    "Failed to recreate documents_project folder: %s. "
                    "Skipping document folder creation.", create_err
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
