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
                self.env.user.notify_warning(
                    message=_("Warning: Only %s invoices left!") % left,
                    title=_("Quota Warning"),
                    sticky=True
                )
            else:
                self.env.user.notify_info(
                    message=_("You have %s invoices left.") % left,
                    title=_("Quota Info"),
                    sticky=False
                )
        return res 