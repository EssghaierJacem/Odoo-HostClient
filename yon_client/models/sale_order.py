from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].get_singleton()
        if plan and plan.max_quotations > 0:
            used = self.env['sale.order'].search_count([])
            left = plan.max_quotations - used
            if left <= 0:
                raise UserError(_("You have reached your quotation quota (%d)." % plan.max_quotations))
        res = super().create(vals)
        left = plan.max_quotations - self.env['sale.order'].search_count([])
        message = _('You have %s quotations left.') % left
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