# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectTaskTemplate(models.Model):
    _name = 'ics.project.task.template'
    _description = 'Project Task Template'
    _order = 'sequence, id'

    name = fields.Char('Template Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    
    tender_category = fields.Selection([
        ('supply', 'Supply'),
        ('services', 'Services'),
        ('construction', 'Construction'),
        ('maintenance', 'Maintenance & Operation'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ], string='Applicable to Tender Category', 
        help='Leave empty to apply to all categories')
    
    task_line_ids = fields.One2many('ics.project.task.template.line', 
        'template_id', string='Tasks')
    
    task_count = fields.Integer('Number of Tasks', compute='_compute_task_count')
    
    @api.depends('task_line_ids')
    def _compute_task_count(self):
        for template in self:
            template.task_count = len(template.task_line_ids)


class ProjectTaskTemplateLine(models.Model):
    _name = 'ics.project.task.template.line'
    _description = 'Project Task Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one('ics.project.task.template', 
        string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Task Name', required=True, translate=True)
    description = fields.Html('Description', translate=True)
    
    stage_id = fields.Many2one('project.task.type', string='Stage',
        help='Initial stage for this task')
    
    user_id = fields.Many2one('res.users', string='Assigned To',
        help='Default assignee (can be overridden at project creation)')
    
    tag_ids = fields.Many2many('project.tags', string='Tags')
    
    planned_hours = fields.Float('Planned Hours', help='Estimated hours for this task')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1')
    
    delay_days = fields.Integer('Start After (Days)', default=0,
        help='Number of days after project start to create this task')
