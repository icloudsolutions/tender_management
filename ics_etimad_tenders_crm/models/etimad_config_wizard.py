# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EtimadConfigWizard(models.TransientModel):
    """Dedicated configuration form for Smart Matching (Preferred Activities, etc.).

    Use this form to avoid the 'Invalid fields: Document, Spreadsheet, Folder'
    error that can occur when the main Settings form loads fields from other
    installed modules (Documents/Spreadsheet). This wizard only contains
    Etimad fields and reads/writes the same res.company and ir.config_parameter
    storage as the main settings.
    """
    _name = 'ics.etimad.config.wizard'
    _description = 'Etimad Smart Matching Configuration'

    etimad_enable_matching = fields.Boolean(
        string="Enable Smart Matching",
        default=True,
        help="Calculate matching scores for tenders based on company profile",
    )
    etimad_preferred_activities_ids = fields.Many2many(
        'ics.etimad.activity',
        'ics_etimad_config_wizard_activity_rel',
        'wizard_id',
        'activity_id',
        string="Preferred Activities",
        help="Select your company's main business activities from Etimad classification.",
    )
    etimad_preferred_categories = fields.Char(
        string="Primary Business Categories",
        help="Comma-separated: supply, services, construction, maintenance, consulting",
    )
    etimad_preferred_agencies = fields.Char(
        string="Preferred Agencies",
        help="Comma-separated agency names for higher match scores",
    )
    etimad_min_preparation_days = fields.Integer(
        string="Min Preparation Days",
        default=7,
        help="Minimum days needed to prepare a tender submission",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        company = self.env.company
        params = self.env['ir.config_parameter'].sudo()
        if 'etimad_enable_matching' in fields_list:
            res['etimad_enable_matching'] = params.get_param(
                'ics_etimad_tenders_crm.etimad_enable_matching', 'True'
            ) == 'True'
        if 'etimad_preferred_activities_ids' in fields_list:
            res['etimad_preferred_activities_ids'] = [(6, 0, company.etimad_preferred_activities_ids.ids)]
        if 'etimad_preferred_categories' in fields_list:
            res['etimad_preferred_categories'] = params.get_param(
                'ics_etimad_tenders_crm.etimad_preferred_categories', ''
            )
        if 'etimad_preferred_agencies' in fields_list:
            res['etimad_preferred_agencies'] = params.get_param(
                'ics_etimad_tenders_crm.etimad_preferred_agencies', ''
            )
        if 'etimad_min_preparation_days' in fields_list:
            val = params.get_param('ics_etimad_tenders_crm.etimad_min_preparation_days', '7')
            res['etimad_min_preparation_days'] = int(val or 7)
        return res

    def action_save(self):
        self.ensure_one()
        company = self.env.company
        params = self.env['ir.config_parameter'].sudo()
        company.sudo().write({
            'etimad_preferred_activities_ids': [(6, 0, self.etimad_preferred_activities_ids.ids)],
        })
        params.set_param('ics_etimad_tenders_crm.etimad_enable_matching', str(self.etimad_enable_matching))
        params.set_param('ics_etimad_tenders_crm.etimad_preferred_categories', self.etimad_preferred_categories or '')
        params.set_param('ics_etimad_tenders_crm.etimad_preferred_agencies', self.etimad_preferred_agencies or '')
        params.set_param('ics_etimad_tenders_crm.etimad_min_preparation_days', str(self.etimad_min_preparation_days))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Configuration saved',
                'message': 'Smart Matching settings have been saved.',
                'type': 'success',
                'sticky': False,
            },
        }
