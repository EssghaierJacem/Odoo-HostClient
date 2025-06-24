from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].get_singleton()
        if plan and plan.max_invoices > 0 and vals.get('move_type') == 'out_invoice':
            used = self.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            left = plan.max_invoices - used
            if left <= 0:
                raise UserError(_("You have reached your invoice quota (%d)." % plan.max_invoices))
        res = super().create(vals)
        if vals.get('move_type') == 'out_invoice':
            left = plan.max_invoices - self.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            message = _('You have %s invoices left.') % left
            notif_type = 'warning' if left <= 3 else 'info'
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
        return res 