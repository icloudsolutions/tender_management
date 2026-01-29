from odoo import models, fields, api


class TenderStage(models.Model):
    _name = 'ics.tender.stage'
    _description = 'Tender Stage'
    _order = 'sequence, id'

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    fold = fields.Boolean('Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    is_won = fields.Boolean('Is Won Stage')
    is_lost = fields.Boolean('Is Lost Stage')
    requirements = fields.Html('Requirements',
        help='Enter the requirements needed to move to this stage')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Stage name must be unique!'),
    ]
