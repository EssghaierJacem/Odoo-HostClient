from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].search([], limit=1)
        if plan and plan.max_invoices > 0:
            if plan.invoices_left <= 0:
                raise UserError(_("You have reached your invoice quota (%d).") % plan.max_invoices)
        res = super().create(vals)
        if plan:
            left = plan.invoices_left
            if left <= 3:
                color = 'danger'
                message = _('Warning: Only %s invoices left!') % left
            else:
                color = 'success'
                message = _('You have %s invoices left.') % left
            res.env.user.notify_info(message, title=_('Quota Info'), sticky=True, type=color)
        return res 