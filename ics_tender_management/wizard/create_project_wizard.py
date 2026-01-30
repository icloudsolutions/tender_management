from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class CreateProjectWizard(models.TransientModel):
    _name = 'ics.tender.project.wizard'
    _description = 'Create Project from Tender'

    tender_id = fields.Many2one('ics.tender', string='Tender', required=True, readonly=True)

    name = fields.Char('Project Name', required=True)

    partner_id = fields.Many2one('res.partner', string='Customer',
        related='tender_id.partner_id', readonly=True)

    user_id = fields.Many2one('res.users', string='Project Manager',
        default=lambda self: self.env.user)

    sale_order_id = fields.Many2one('sale.order', string='Sales Order',
        domain="[('tender_id', '=', tender_id), ('state', 'in', ['sale', 'done'])]")

    create_from_boq = fields.Boolean('Create Tasks from BoQ',
        default=True, help='Create project tasks from tender BoQ lines')

    create_from_sale_order = fields.Boolean('Link to Sales Order',
        default=True, help='Link project to sales order if available')

    date_start = fields.Date('Start Date', default=fields.Date.today)
    
    task_template_id = fields.Many2one('ics.project.task.template', 
        string='Task Template',
        help='Select a task template to automatically create predefined project tasks')
    
    use_task_template = fields.Boolean('Use Task Template', default=True,
        help='Create tasks from template instead of BoQ')

    @api.model
    def default_get(self, fields_list):
        res = super(CreateProjectWizard, self).default_get(fields_list)
        if self._context.get('default_tender_id'):
            tender = self.env['ics.tender'].browse(self._context['default_tender_id'])
            res['name'] = f"Project - {tender.tender_title}"

            confirmed_orders = self.env['sale.order'].search([
                ('tender_id', '=', tender.id),
                ('state', 'in', ['sale', 'done'])
            ], limit=1)
            if confirmed_orders:
                res['sale_order_id'] = confirmed_orders[0].id
            
            # Auto-select template based on tender category
            if tender.tender_category:
                template = self.env['ics.project.task.template'].search([
                    ('tender_category', '=', tender.tender_category),
                    ('active', '=', True)
                ], limit=1)
                if template:
                    res['task_template_id'] = template.id
            
            # If no category-specific template, get general template
            if not res.get('task_template_id'):
                general_template = self.env['ics.project.task.template'].search([
                    ('tender_category', '=', False),
                    ('active', '=', True)
                ], limit=1)
                if general_template:
                    res['task_template_id'] = general_template.id
        return res
    
    @api.onchange('use_task_template')
    def _onchange_use_task_template(self):
        """Toggle between template and BoQ task creation"""
        if self.use_task_template:
            self.create_from_boq = False
        else:
            self.create_from_boq = True

    def action_create_project(self):
        self.ensure_one()

        if self.tender_id.state != 'won':
            raise UserError(_('Only won tenders can be converted to projects.'))

        project_vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'tender_id': self.tender_id.id,
            'date_start': self.date_start,
        }

        if self.sale_order_id and self.create_from_sale_order:
            project_vals['sale_order_id'] = self.sale_order_id.id
            project_vals['sale_line_id'] = self.sale_order_id.order_line[0].id if self.sale_order_id.order_line else False

        project = self.env['project.project'].create(project_vals)

        # Create tasks from template
        if self.use_task_template and self.task_template_id:
            self._create_tasks_from_template(project)
        # Or create tasks from BoQ
        elif self.create_from_boq and self.tender_id.boq_line_ids:
            for boq_line in self.tender_id.boq_line_ids:
                self.env['project.task'].create({
                    'name': boq_line.name,
                    'project_id': project.id,
                    'partner_id': self.partner_id.id,
                    'user_ids': [(6, 0, [self.user_id.id])],
                    'description': boq_line.specifications if boq_line.specifications else boq_line.notes,
                })

        return {
            'name': _('Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': project.id,
            'target': 'current',
        }
