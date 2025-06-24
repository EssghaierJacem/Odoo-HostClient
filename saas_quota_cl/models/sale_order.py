from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].search([], limit=1)
        if plan and plan.max_quotations > 0:
            if plan.quotations_left <= 0:
                raise UserError(_("You have reached your quotation quota (%d).") % plan.max_quotations)
        return super().create(vals) 