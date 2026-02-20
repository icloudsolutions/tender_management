# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SmbCreateProjectWizard(models.TransientModel):
    _name = 'smb.create.project.wizard'
    _description = 'Create Delivery Project from Sale Order'

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, readonly=True)
    name = fields.Char(string='Project Name', required=True)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', readonly=True)
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
    date_start = fields.Date(string='Start Date', default=fields.Date.context_today)

    use_task_template = fields.Boolean(
        string='Use Task Template',
        default=True,
        help='Create project tasks from the selected template.',
    )
    task_template_id = fields.Many2one(
        'smb.project.task.template',
        string='Task Template',
        domain=[('active', '=', True)],
        help='Select a template to create predefined tasks in the project.',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self._context.get('active_id') or self._context.get('default_order_id')
        if order_id:
            order = self.env['sale.order'].browse(order_id)
            if order.exists():
                res['order_id'] = order.id
                res['name'] = _('Delivery - %s - %s') % (order.name, order.partner_id.name or '')
                company = order.company_id or self.env.company
                if getattr(company, 'smb_default_project_template_id', None):
                    res['task_template_id'] = company.smb_default_project_template_id.id
        return res

    def action_create_project(self):
        self.ensure_one()
        if self.order_id.state not in ('sale', 'done'):
            raise UserError(_('Only confirmed Sale Orders can have a delivery project.'))
        # Check if project already linked (sale_order_id exists on project in ics_tender_management or we add it)
        existing = self.env['project.project'].search([('sale_order_id', '=', self.order_id.id)], limit=1)
        if existing:
            raise UserError(_('A project is already linked to this order: %s') % existing.name)
        project_vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'sale_order_id': self.order_id.id,
            'date_start': self.date_start,
        }
        project = self.env['project.project'].create(project_vals)
        if self.use_task_template and self.task_template_id:
            self._create_tasks_from_template(project)
        self.order_id.message_post(
            body=_('Delivery project created: <a href="/web#id=%s&model=project.project&view_type=form">%s</a>')
            % (project.id, project.name),
            body_is_html=True,
        )
        return {
            'name': _('Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': project.id,
            'target': 'current',
        }

    def _create_tasks_from_template(self, project):
        self.ensure_one()
        if not self.task_template_id or not self.task_template_id.task_line_ids:
            return
        project_start = self.date_start or fields.Date.context_today(self)
        for line in self.task_template_id.task_line_ids:
            task_vals = {
                'name': line.name,
                'project_id': project.id,
                'partner_id': self.partner_id.id,
                'description': line.description,
                'priority': line.priority,
                'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                'planned_hours': line.planned_hours,
            }
            if line.delay_days > 0:
                task_vals['date_deadline'] = project_start + timedelta(days=line.delay_days)
            if line.user_id:
                task_vals['user_ids'] = [(6, 0, [line.user_id.id])]
            elif self.user_id:
                task_vals['user_ids'] = [(6, 0, [self.user_id.id])]
            if line.stage_id:
                task_vals['stage_id'] = line.stage_id.id
            self.env['project.task'].create(task_vals)
