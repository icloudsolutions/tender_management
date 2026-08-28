# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class EtimadMatchingRule(models.Model):
    _name = 'ics.etimad.matching.rule'
    _description = 'Etimad Tender Smart Matching Rule'
    _order = 'sequence, id'

    name = fields.Char('Rule Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    # Condition
    field_name = fields.Selection(
        [
            ('name', 'Tender Name'),
            ('agency_name', 'Agency Name'),
            ('activity_name', 'Activity Name'),
            ('etimad_tender_type', 'Tender Type'),
            ('description', 'Description'),
            ('estimated_amount', 'Estimated Amount'),
            ('remaining_days', 'Remaining Days'),
            ('document_cost_amount', 'Document Cost'),
            ('contract_duration_days', 'Contract Duration (Days)'),
            ('tender_purpose', 'Tender Purpose'),
            ('activity_details', 'Activity Details'),
            ('execution_regions', 'Execution Regions'),
            ('execution_cities', 'Execution Cities'),
        ],
        string='Field',
        required=True,
    )
    operator = fields.Selection(
        [
            ('contains', 'Contains'),
            ('not_contains', 'Does Not Contain'),
            ('equals', 'Equals'),
            ('not_equals', 'Not Equals'),
            ('startswith', 'Starts With'),
            ('endswith', 'Ends With'),
            ('regex', 'Regex Match'),
            ('in_list', 'In List (comma-separated)'),
            ('gt', 'Greater Than'),
            ('gte', 'Greater or Equal'),
            ('lt', 'Less Than'),
            ('lte', 'Less or Equal'),
            ('is_empty', 'Is Empty'),
            ('is_not_empty', 'Is Not Empty'),
        ],
        string='Operator',
        required=True,
        default='contains',
    )
    value_char = fields.Char('Value (text)')
    value_float = fields.Float('Value (number)')

    # Action
    action_type = fields.Selection(
        [
            ('assign_user', 'Assign to User'),
            ('set_favorite', 'Mark as Favorite'),
            ('add_note', 'Append to Internal Notes'),
            ('add_reason', 'Append to Match Reasons'),
        ],
        string='Action',
        required=True,
    )
    user_id = fields.Many2one('res.users', 'Assign to', help='Used when Action is "Assign to User".')
    action_value_char = fields.Char('Value', help='Used for note text or match reason text.')

    @api.constrains('field_name', 'operator', 'value_char', 'value_float')
    def _check_value_required(self):
        numeric_ops = ('gt', 'gte', 'lt', 'lte')
        text_ops = ('contains', 'not_contains', 'equals', 'not_equals', 'startswith', 'endswith', 'regex', 'in_list')
        numeric_fields = ('estimated_amount', 'remaining_days', 'document_cost_amount', 'contract_duration_days')
        for rule in self:
            if rule.operator in ('is_empty', 'is_not_empty'):
                continue
            if rule.operator in numeric_ops:
                if rule.field_name not in numeric_fields:
                    raise ValidationError(
                        _('Operator "%s" can only be used with numeric fields (Estimated Amount, Remaining Days, etc.).')
                        % rule.operator
                    )
            if rule.operator in text_ops:
                if rule.field_name in numeric_fields:
                    if not rule.value_char and rule.value_float == 0.0:
                        raise ValidationError(_('Please set Value (text) or Value (number) for this condition.'))
                elif not (rule.value_char and rule.value_char.strip()):
                    raise ValidationError(_('Please set Value (text) for this condition.'))

    def _tender_value_for_field(self, tender, field_name):
        """Get tender field value for comparison (string for text, number for numeric)."""
        if field_name in ('estimated_amount', 'remaining_days', 'document_cost_amount', 'contract_duration_days'):
            val = getattr(tender, field_name, None)
            return (val is not None and val or 0) if isinstance(val, (int, float)) else 0
        val = getattr(tender, field_name, None)
        return (val or '').strip() if val is not None else ''

    def _condition_matches(self, tender):
        """Return True if the tender matches this rule's condition."""
        self.ensure_one()
        field_val = self._tender_value_for_field(tender, self.field_name)
        op = self.operator
        is_numeric = self.field_name in ('estimated_amount', 'remaining_days', 'document_cost_amount', 'contract_duration_days')

        if op == 'is_empty':
            if is_numeric:
                return field_val == 0 or field_val is None
            return (field_val or '') == ''
        if op == 'is_not_empty':
            if is_numeric:
                return field_val != 0 and field_val is not None
            return bool(field_val or '')

        if op in ('gt', 'gte', 'lt', 'lte'):
            try:
                compare = float(self.value_float) if self.value_char in (None, '') else float(self.value_char.replace(',', '.').strip())
            except (TypeError, ValueError):
                compare = 0
            actual = float(field_val) if field_val not in (None, '') else 0
            if op == 'gt':
                return actual > compare
            if op == 'gte':
                return actual >= compare
            if op == 'lt':
                return actual < compare
            if op == 'lte':
                return actual <= compare

        # Text comparisons (normalize to string and optionally case-insensitive)
        text_val = str(field_val).strip() if field_val is not None else ''
        compare = (self.value_char or '').strip()

        if op == 'contains':
            return compare.lower() in text_val.lower()
        if op == 'not_contains':
            return compare.lower() not in text_val.lower()
        if op == 'equals':
            return text_val.lower() == compare.lower()
        if op == 'not_equals':
            return text_val.lower() != compare.lower()
        if op == 'startswith':
            return text_val.lower().startswith(compare.lower())
        if op == 'endswith':
            return text_val.lower().endswith(compare.lower())
        if op == 'regex':
            if not compare:
                return False
            try:
                return bool(re.search(compare, text_val, re.IGNORECASE))
            except re.error:
                return False
        if op == 'in_list':
            if not compare:
                return False
            items = [x.strip().lower() for x in compare.split(',') if x.strip()]
            return text_val.lower() in items
        return False

    def _get_action_updates(self, tender):
        """If condition matches, return a dict of {field: value} to write on the tender. Else return None."""
        self.ensure_one()
        if not self._condition_matches(tender):
            return None
        if self.action_type == 'assign_user' and self.user_id:
            return {'assigned_user_id': self.user_id.id}
        if self.action_type == 'set_favorite':
            return {'is_favorite': True}
        if self.action_type == 'add_note' and self.action_value_char:
            new_note = (self.action_value_char or '').strip()
            if new_note:
                existing = (tender.notes or '').strip()
                return {'notes': f"{existing}\n{new_note}".strip() if existing else new_note}
        if self.action_type == 'add_reason' and self.action_value_char:
            new_reason = (self.action_value_char or '').strip()
            if new_reason:
                existing = (tender.dynamic_match_reasons or '').strip()
                return {'dynamic_match_reasons': f"{existing}\n{new_reason}".strip() if existing else new_reason}
        return None
