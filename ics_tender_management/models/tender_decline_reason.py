# -*- coding: utf-8 -*-
from odoo import models, fields


class TenderDeclineReason(models.Model):
    _name = 'ics.tender.decline.reason'
    _description = 'Tender Decline Reason'
    _order = 'sequence, id'

    name = fields.Char('Reason', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
