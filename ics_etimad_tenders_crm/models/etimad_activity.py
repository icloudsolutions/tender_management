from odoo import models, fields, api


class EtimadActivity(models.Model):
    _name = 'ics.etimad.activity'
    _description = 'Etimad Tender Activities'
    _order = 'activity_id'
    
    activity_id = fields.Integer(
        string='Activity ID',
        required=True,
        help='Etimad activity ID from the portal'
    )
    
    name = fields.Char(
        string='Activity Name (Arabic)',
        required=True,
        translate=True,
        help='Activity name as displayed in Etimad portal'
    )
    
    name_en = fields.Char(
        string='Activity Name (English)',
        help='English translation of the activity name'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to hide this activity from selection'
    )
    
    # Keywords for matching
    keywords = fields.Text(
        string='Matching Keywords',
        help='Comma-separated keywords for tender matching (Arabic and English)'
    )
    
    # Color for visualization (optional)
    color = fields.Integer(string='Color Index')
    
    _sql_constraints = [
        ('activity_id_unique', 'UNIQUE(activity_id)', 'Activity ID must be unique!')
    ]
    
    @api.depends('name', 'name_en')
    def _compute_display_name(self):
        """Display both Arabic and English names if available (Odoo 18 compatible)"""
        for record in self:
            if record.name_en:
                record.display_name = f"{record.name} - {record.name_en}"
            else:
                record.display_name = record.name or ''
