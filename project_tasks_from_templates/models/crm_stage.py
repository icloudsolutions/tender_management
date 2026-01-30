# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, models


class CrmStage(models.Model):
    """Inherit crm.stage to auto-create project templates."""
    _inherit = 'crm.stage'
    _description = 'CRM Stage (Extended)'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-create project template if setting is enabled."""
        stages = super().create(vals_list)
        if self.env['ir.config_parameter'].sudo().get_param(
                'project_tasks_from_templates.auto_create_template_from_crm_stage'):
            for stage in stages:
                self._create_project_template_from_crm_stage(stage)
        return stages

    def write(self, vals):
        """Override write to auto-create/update project template if setting is enabled."""
        result = super().write(vals)
        if self.env['ir.config_parameter'].sudo().get_param(
                'project_tasks_from_templates.auto_create_template_from_crm_stage'):
            for stage in self:
                self._create_project_template_from_crm_stage(stage)
        return result

    def _create_project_template_from_crm_stage(self, crm_stage):
        """
        Create or update a project template from a CRM stage.

        Args:
            crm_stage (recordset): The CRM stage record.
        """
        # Check if a template already exists for this CRM stage
        existing_template = self.env['project.task.template'].search([
            ('name', '=', f'Template from CRM Stage: {crm_stage.name}')
        ], limit=1)

        if existing_template:
            # Update existing template name if CRM stage name changed
            if existing_template.name != f'Template from CRM Stage: {crm_stage.name}':
                existing_template.name = f'Template from CRM Stage: {crm_stage.name}'
        else:
            # Create new project template
            template = self.env['project.task.template'].create({
                'name': f'Template from CRM Stage: {crm_stage.name}',
            })

            # Try to find or create a corresponding project task type (stage)
            project_stage = self.env['project.task.type'].search([
                ('name', '=', crm_stage.name)
            ], limit=1)

            if not project_stage:
                # Create a new project task type matching the CRM stage
                project_stage = self.env['project.task.type'].create({
                    'name': crm_stage.name,
                    'sequence': crm_stage.sequence or 0,
                })

            # Create a project.stage record linking the template to the project stage
            self.env['project.stage'].create({
                'project_template_id': template.id,
                'project_stage_id': project_stage.id,
                'sequence': crm_stage.sequence or 0,
            })
