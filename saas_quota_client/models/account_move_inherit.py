from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        plan = self.env['subscription.plan'].search([], limit=1)
        if plan:
            left = plan.max_invoices - plan.used_invoices
            if left <= 3:
                color = 'danger'
                message = _('Warning: Only %s invoices left!') % left
            else:
                color = 'success'
                message = _('You have %s invoices left.') % left
            res.env.user.notify_info(message, title=_('Quota Info'), sticky=True, type=color)
        return res 