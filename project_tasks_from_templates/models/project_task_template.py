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
from odoo import fields, models


class ProjectTaskTemplate(models.Model):
    """A model to define task templates for projects."""
    _name = 'project.task.template'
    _description = 'Project Task Template'

    name = fields.Char(string='Template Name', translate=True,
                       help='Name for the task template.')
    task_ids = fields.One2many(
        'project.sub.task', 'project_template_id',
        string='Tasks',
        help='List of the tasks associated with this template.')
    stage_ids = fields.One2many(
        'project.stage', 'project_template_id',
        string='Stages',
        help='List of the stages associated with this template.')
    
    # CRM Integration fields
    crm_stage_id = fields.Many2one(
        'crm.stage',
        string='Auto-create on CRM Stage',
        help='Automatically create a project from this template when a CRM opportunity reaches this stage.')
    auto_create_project = fields.Boolean(
        string='Auto-create Project from CRM',
        default=False,
        help='Enable automatic project creation when CRM opportunity reaches the configured stage.')