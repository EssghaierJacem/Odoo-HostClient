from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].get_singleton()
        if plan and plan.max_invoices > 0:
            used = self.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            if plan.max_invoices - used <= 0:
                raise UserError(_("You have reached your invoice quota (%d).") % plan.max_invoices)
        return super().create(vals)

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].search([], limit=1)
        if plan and plan.max_invoices > 0:
            if plan.max_invoices - plan.env['account.move'].search_count([('move_type', '=', 'out_invoice')]) <= 0:
                raise UserError(_("You have reached your invoice quota (%d).") % plan.max_invoices)
        res = super().create(vals)
        left = plan.max_invoices - plan.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
        if left <= 3:
            message = _('Warning: Only %s invoices left!') % left
            notif_type = 'warning'
        else:
            message = _('You have %s invoices left.') % left
            notif_type = 'info'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Quota Info'),
                'message': message,
                'type': notif_type,
                'sticky': False,
            }
        } 