# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # SMB Credit Control workflow (SMB-SOP-1)
    smb_credit_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent_to_credit', 'Sent to Credit Control'),
            ('credit_approved', 'Credit Approved'),
            ('credit_rejected', 'Credit Rejected'),
        ],
        string='Credit State',
        default='draft',
        copy=False,
        tracking=True,
        help='SMB workflow: Draft → Sent to Credit Control → Approved/Rejected',
    )
    smb_credit_approved_by = fields.Many2one(
        'res.users',
        string='Credit Approved By',
        readonly=True,
        copy=False,
    )
    smb_credit_approved_date = fields.Datetime(
        string='Credit Approved Date',
        readonly=True,
        copy=False,
    )
    smb_credit_reject_reason = fields.Text(
        string='Credit Reject Reason',
        readonly=True,
        copy=False,
        help='Reason for rejection: e.g. overdue payments, credit limit exceeded. '
             'Sales person informs customer and requests payment clearance.',
    )
    smb_critical_order = fields.Boolean(
        string='Critical Order',
        default=False,
        help='If set, sales coordinates with logistics for timely delivery.',
    )
    warranty_years = fields.Selection(
        selection=[
            ('1', '1 Year'),
            ('2', '2 Years'),
            ('3', '3 Years'),
        ],
        string='Warranty (Years)',
        copy=True,
        help='Warranty period in years. This is added explicitly to Terms and Conditions.',
    )

    def _smb_warranty_sentence(self, years):
        """Return the explicit warranty clause for terms and conditions."""
        if not years:
            return ''
        try:
            n = int(years)
        except (TypeError, ValueError):
            return ''
        year_label = _('%s year', 'Warranty years') % n if n == 1 else _('%s years', 'Warranty years') % n
        return _('Warranty: %s from the date of delivery.', 'Terms and conditions clause') % year_label

    def _smb_note_apply_warranty(self, note, warranty_years):
        """Ensure note contains exactly one warranty sentence; remove old, append new if years set."""
        if not note:
            note = ''
        prefix = 'Warranty:'
        lines = []
        for line in note.splitlines():
            stripped = line.strip()
            if stripped.startswith(prefix):
                continue
            lines.append(line)
        base = '\n'.join(lines).rstrip()
        sentence = self._smb_warranty_sentence(warranty_years) if warranty_years else ''
        if not sentence:
            return base
        return base + ('\n\n' if base else '') + sentence

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'warranty_years' in vals:
                vals['note'] = self._smb_note_apply_warranty(
                    vals.get('note') or '', vals.get('warranty_years')
                )
        return super().create(vals_list)

    def write(self, vals):
        if 'warranty_years' in vals and 'note' not in vals:
            warranty_years = vals['warranty_years']
            for order in self:
                new_note = order._smb_note_apply_warranty(order.note or '', warranty_years)
                super(SaleOrder, order).write(dict(vals, note=new_note))
            return True
        if 'warranty_years' in vals and 'note' in vals:
            if len(self) == 1:
                vals['note'] = self._smb_note_apply_warranty(
                    vals['note'] or '', vals['warranty_years']
                )
            else:
                for order in self:
                    super(SaleOrder, order).write(dict(
                        vals,
                        note=order._smb_note_apply_warranty(order.note or '', vals['warranty_years']),
                    ))
                return True
        return super().write(vals)

    def action_smb_send_to_credit(self):
        """Sales: send quotation to Credit Control for approval (SMB-SOP-1)."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(
                    _('Only draft or sent quotations can be sent to Credit Control.')
                )
            if order.smb_credit_state not in ('draft', 'credit_rejected'):
                raise UserError(
                    _('This order is already in Credit Control or approved.')
                )
        self.write({'smb_credit_state': 'sent_to_credit'})
        # Optional: create activity for Credit Control
        self._smb_create_credit_activity()
        return True

    def _smb_create_credit_activity(self):
        """Create an activity for Credit Control to review (if mail is available)."""
        if not self.env.ref('ics_smb_management.group_smb_credit_control', raise_if_not_found=False):
            return
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        for order in self:
            order.activity_schedule(
                activity_type_id=activity_type.id,
                summary=_('Credit Control: Review P.O.'),
                note=_('Please review this order for credit approval (customer: %s).')
                % (order.partner_id.name or ''),
                user_id=False,  # assign to Credit Control group (first user or leave unassigned)
            )

    def action_smb_credit_approve(self):
        """Credit Control: approve P.O. (payment history and limit OK)."""
        self.ensure_one()
        if self.smb_credit_state != 'sent_to_credit':
            raise UserError(_('Only orders in "Sent to Credit Control" can be approved.'))
        self._smb_check_credit_before_approve()
        self.write({
            'smb_credit_state': 'credit_approved',
            'smb_credit_approved_by': self.env.user.id,
            'smb_credit_approved_date': fields.Datetime.now(),
            'smb_credit_reject_reason': False,
        })
        self._smb_unlink_credit_activity()
        return True

    def action_smb_open_reject_wizard(self):
        """Open wizard to enter reject reason (Credit Control)."""
        self.ensure_one()
        return {
            'name': _('Reject Credit'),
            'type': 'ir.actions.act_window',
            'res_model': 'smb.credit.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_smb_credit_reject(self, reason=None):
        """Credit Control: reject P.O. (overdue or limit exceeded). Sales is notified."""
        self.ensure_one()
        if self.smb_credit_state != 'sent_to_credit':
            raise UserError(_('Only orders in "Sent to Credit Control" can be rejected.'))
        self.write({
            'smb_credit_state': 'credit_rejected',
            'smb_credit_reject_reason': reason or _('Rejected by Credit Control. '
                'Please follow up with customer for payment clearance or credit limit increase.'),
            'smb_credit_approved_by': False,
            'smb_credit_approved_date': False,
        })
        self._smb_unlink_credit_activity()
        return True

    def _smb_check_credit_before_approve(self):
        """Optional: check partner credit limit and overdue. Override to enforce strict checks."""
        partner = self.partner_id
        if not partner:
            return
        # Use standard credit fields if available (account module)
        credit_limit = getattr(partner, 'credit_limit', 0) or 0
        credit = getattr(partner, 'credit', 0) or 0
        amount_total = self.amount_total
        if credit_limit and (credit + amount_total) > credit_limit:
            raise ValidationError(
                _('Credit limit exceeded for %s. Current exposure: %s; Order total: %s; Limit: %s. '
                  'Request credit limit increase or payment clearance.')
                % (partner.name, credit, amount_total, credit_limit)
            )

    def _smb_unlink_credit_activity(self):
        """Remove the 'Review P.O.' activity when approved or rejected."""
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        self.env['mail.activity'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type.id),
            ('summary', 'ilike', 'Credit Control'),
        ]).unlink()

    def action_smb_create_project(self):
        """Open wizard to create delivery project from this order (SMB / Project integration)."""
        self.ensure_one()
        return {
            'name': _('Create Delivery Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'smb.create.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'active_id': self.id},
        }

    def action_smb_reset_credit(self):
        """Sales: reset to draft credit state (e.g. after customer cleared payments)."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('Only draft or sent quotations can be reset for credit.'))
        self.write({
            'smb_credit_state': 'draft',
            'smb_credit_reject_reason': False,
            'smb_credit_approved_by': False,
            'smb_credit_approved_date': False,
        })
        return True

    def action_confirm(self):
        """Enforce: when company requires it, only allow confirm when credit is approved (SMB workflow)."""
        for order in self:
            company = order.company_id or self.env.company
            if not getattr(company, 'smb_require_credit_approval', False):
                continue
            # Require credit_approved: block draft (never sent), sent_to_credit (pending), credit_rejected
            if order.smb_credit_state != 'credit_approved':
                if order.smb_credit_state == 'sent_to_credit':
                    raise UserError(
                        _('This order is pending Credit Control approval. It cannot be confirmed yet.')
                    )
                if order.smb_credit_state == 'credit_rejected':
                    raise UserError(
                        _('This order was rejected by Credit Control. '
                          'Reset credit state after payment clearance, then resend to Credit Control.')
                    )
                # draft or any other: must go through credit first
                raise UserError(
                    _('Credit approval is required before confirming. Send this quotation to Credit Control first (Send to Credit), then confirm after approval.')
                )
        return super().action_confirm()

    # -------------------------------------------------------------------------
    # Collection (SMB-SOP-1): monthly SoA reminder & escalate overdue to Sales
    # -------------------------------------------------------------------------

    @api.model
    def _cron_smb_monthly_soa_reminder(self):
        """Create activities to send monthly Statement of Account to credit customers."""
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        # Partners with receivable balance (posted move lines, receivable account)
        AccountMoveLine = self.env['account.move.line']
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('balance', '>', 0),
            ('partner_id', '!=', False),
        ]
        lines = AccountMoveLine.search_read(domain, ['partner_id'], order='partner_id')
        partner_ids = list({line['partner_id'][0] for line in lines if line.get('partner_id')})
        if not partner_ids:
            return
        summary = _('Send monthly Statement of Account (SoA)')
        note = _('SMB Collection: Send Statement of Account to this credit customer.')
        for partner in self.env['res.partner'].browse(partner_ids):
            # Avoid duplicate open activity
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner.id),
                ('summary', '=', summary),
            ], limit=1)
            if not existing:
                partner.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=summary,
                    note=note,
                    user_id=False,
                )

    @api.model
    def _cron_smb_escalate_overdue_to_sales(self):
        """Create activities for Sales when invoices are overdue (escalate to Sales)."""
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        today = fields.Date.context_today(self)
        moves = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<', today),
            ('partner_id', '!=', False),
        ])
        summary = _('Payment follow-up - escalated to Sales (SMB)')
        for move in moves:
            user_id = getattr(move.partner_id, 'user_id', None) and move.partner_id.user_id.id or False
            if not user_id and move.line_ids:
                sale_lines = move.line_ids.mapped('sale_line_ids')
                orders = sale_lines.mapped('order_id')
                if orders and orders[0].user_id:
                    user_id = orders[0].user_id.id
            if not user_id:
                continue
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', move.id),
                ('summary', 'ilike', 'escalated to Sales'),
            ], limit=1)
            if not existing:
                move.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=summary,
                    note=_('Overdue invoice. Please follow up with customer (SMB Collection).'),
                    user_id=user_id,
                )
