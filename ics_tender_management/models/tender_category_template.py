# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


# Same selection as ics.tender.tender_category
TENDER_CATEGORY_SELECTION = [
    ('supply', 'Supply'),
    ('services', 'Services'),
    ('construction', 'Construction'),
    ('maintenance', 'Maintenance & Operation'),
    ('consulting', 'Consulting'),
    ('other', 'Other'),
]


class TenderCategoryTemplateMapping(models.Model):
    _name = 'ics.tender.category.template.mapping'
    _description = 'Tender Category to Project Template Mapping'
    _order = 'tender_category'

    tender_category = fields.Selection(
        TENDER_CATEGORY_SELECTION,
        string='Tender Category',
        required=True,
        help='When a tender with this category is won, the chosen template is used to auto-create the project.'
    )
    ics_template_id = fields.Many2one(
        'ics.project.task.template',
        string='ICS Task Template',
        ondelete='set null',
        help='Use this ICS task template when a won tender has this category (optional).'
    )
    use_external_template = fields.Boolean(
        'Use External Template',
        default=False,
        help='When checked, use the template from project_tasks_from_templates module instead of ICS template.'
    )
    external_template_id = fields.Integer(
        'External Template ID',
        copy=False,
        help='ID of the project.task.template record (from project_tasks_from_templates).'
    )
    external_template_name = fields.Char(
        'External Template Name',
        compute='_compute_external_template_name',
        readonly=True,
        store=False
    )

    _sql_constraints = [
        ('tender_category_unique', 'UNIQUE(tender_category)',
         'Only one template mapping per tender category.'),
    ]

    @api.depends('external_template_id')
    def _compute_external_template_name(self):
        for rec in self:
            name = ''
            if rec.external_template_id and 'project.task.template' in self.env:
                template = self.env['project.task.template'].sudo().browse(rec.external_template_id)
                if template.exists():
                    name = template.name
            rec.external_template_name = name or _('(Not set)')

    def action_choose_external_template(self):
        """Open wizard to select an external project template."""
        self.ensure_one()
        return {
            'name': _('Select External Project Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.category.template.choose.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_mapping_id': self.id},
        }

    def action_clear_external_template(self):
        self.ensure_one()
        self.write({
            'use_external_template': False,
            'external_template_id': 0,
        })


class TenderCategoryTemplateChooseWizard(models.TransientModel):
    _name = 'ics.tender.category.template.choose.wizard'
    _description = 'Choose External Project Template'

    mapping_id = fields.Many2one(
        'ics.tender.category.template.mapping',
        string='Mapping',
        required=True,
        readonly=True,
        ondelete='cascade'
    )
    external_template_id = fields.Selection(
        selection='_selection_external_templates',
        string='Project Template',
        help='Select a template from project_tasks_from_templates (Project → Configuration → Task Templates).'
    )

    def _selection_external_templates(self):
        if 'project.task.template' not in self.env:
            return [('', _('(Module project_tasks_from_templates not installed)'))]
        templates = self.env['project.task.template'].sudo().search([], order='name')
        return [('', _('-- Select a template --'))] + [(str(t.id), t.name) for t in templates]

    def action_confirm(self):
        self.ensure_one()
        if not self.external_template_id:
            raise UserError(_('Please select a project template.'))
        self.mapping_id.write({
            'use_external_template': True,
            'external_template_id': int(self.external_template_id),
        })
        return {'type': 'ir.actions.act_window_close'}
