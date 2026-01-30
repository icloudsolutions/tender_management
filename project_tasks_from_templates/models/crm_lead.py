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
from odoo import api, fields, models


class CrmLead(models.Model):
    """Inherit crm.lead to auto-create projects from templates."""
    _inherit = 'crm.lead'

    project_ids = fields.One2many(
        'project.project',
        'crm_lead_id',
        string='Projects',
        help='Projects created from this opportunity.')
    project_count = fields.Integer(
        string='Project Count',
        compute='_compute_project_count',
        help='Number of projects created from this opportunity.')

    @api.depends('project_ids')
    def _compute_project_count(self):
        """Compute the number of projects."""
        for lead in self:
            lead.project_count = len(lead.project_ids)

    def write(self, vals):
        """Override write to auto-create project when stage changes."""
        # Store old stage before update
        old_stages = {lead.id: lead.stage_id.id for lead in self}
        result = super().write(vals)
        
        # Check if stage was changed
        if 'stage_id' in vals:
            for lead in self:
                # Only create project if stage actually changed
                if old_stages.get(lead.id) != lead.stage_id.id:
                    self._auto_create_project_from_stage(lead)
        
        return result

    def _auto_create_project_from_stage(self, lead):
        """
        Auto-create project from template when opportunity reaches configured stage.

        Args:
            lead (recordset): The CRM lead/opportunity record.
        """
        # Find templates configured for this CRM stage
        templates = self.env['project.task.template'].search([
            ('crm_stage_id', '=', lead.stage_id.id),
            ('auto_create_project', '=', True)
        ])

        for template in templates:
            # Check if project already exists for this lead and template
            existing_project = self.env['project.project'].search([
                ('crm_lead_id', '=', lead.id),
                ('project_template_id', '=', template.id)
            ], limit=1)

            if not existing_project:
                # Create new project
                project_name = f"{lead.name} - {template.name}"
                project_vals = {
                    'name': project_name,
                    'project_template_id': template.id,
                    'crm_lead_id': lead.id,
                    'partner_id': lead.partner_id.id if lead.partner_id else False,
                    'user_id': lead.user_id.id if lead.user_id else False,
                }

                project = self.env['project.project'].sudo().create(project_vals)

                # Create tasks from template
                project.action_create_project_from_template()

    def action_view_projects(self):
        """Action to view projects created from this opportunity."""
        self.ensure_one()
        return {
            'name': 'Projects',
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [('crm_lead_id', '=', self.id)],
            'context': {'default_crm_lead_id': self.id},
        }
