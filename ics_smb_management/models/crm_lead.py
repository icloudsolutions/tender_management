# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # SMB: use standard Odoo "New Quotation" on opportunity; no extra button needed.
