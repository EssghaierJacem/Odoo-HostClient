from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].get_singleton()
        if plan and plan.max_quotations > 0:
            used = self.env['sale.order'].search_count([])
            if plan.max_quotations - used <= 0:
                raise UserError(_("You have reached your quotation quota (%d).") % plan.max_quotations)
        return super().create(vals)

    @api.model
    def create(self, vals):
        plan = self.env['subscription.plan'].search([], limit=1)
        if plan and plan.max_quotations > 0:
            if plan.max_quotations - plan.env['sale.order'].search_count([]) <= 0:
                raise UserError(_("You have reached your quotation quota (%d).") % plan.max_quotations)
        res = super().create(vals)
        left = plan.max_quotations - plan.env['sale.order'].search_count([])
        if left <= 3:
            message = _('Warning: Only %s quotations left!') % left
            notif_type = 'warning'
        else:
            message = _('You have %s quotations left.') % left
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