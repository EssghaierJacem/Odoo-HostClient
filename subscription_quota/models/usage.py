from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SubscriptionUsage(models.Model):
    _name = 'subscription.usage'
    _description = 'Subscription Usage'

    user_id = fields.Many2one('res.users', required=True)
    plan_id = fields.Many2one('subscription.plan', required=True)
    period = fields.Char(required=True, default=lambda self: fields.Date.today().strftime('%Y-%m'))  # e.g. '2024-06'
    sales_orders = fields.Integer(default=0)
    invoices = fields.Integer(default=0)
    extra_sales_orders = fields.Integer(compute='_compute_extra', store=True)
    extra_invoices = fields.Integer(compute='_compute_extra', store=True)
    total_owed = fields.Float(compute='_compute_total_owed', store=True)

    @api.depends('sales_orders', 'invoices', 'plan_id')
    def _compute_extra(self):
        for rec in self:
            rec.extra_sales_orders = max(0, rec.sales_orders - rec.plan_id.free_sales_orders)
            rec.extra_invoices = max(0, rec.invoices - rec.plan_id.free_invoices)

    @api.depends('extra_sales_orders', 'extra_invoices', 'plan_id')
    def _compute_total_owed(self):
        for rec in self:
            rec.total_owed = (
                rec.plan_id.base_price +
                rec.extra_sales_orders * rec.plan_id.price_per_extra_so +
                rec.extra_invoices * rec.plan_id.price_per_extra_invoice
            )

    @api.model
    def get_or_create_usage(self, user, plan, period):
        usage = self.search([('user_id', '=', user.id), ('plan_id', '=', plan.id), ('period', '=', period)], limit=1)
        if not usage:
            usage = self.create({'user_id': user.id, 'plan_id': plan.id, 'period': period})
        return usage

# Notification helper

def _subscription_notify(self, usage, plan, model):
    msg = _("Plan: %s\nFree SO: %d, Used: %d, Free Inv: %d, Used: %d\nTotal owed: %.2f") % (
        plan.name,
        plan.free_sales_orders, usage.sales_orders,
        plan.free_invoices, usage.invoices,
        usage.total_owed
    )
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _('Subscription Quota'),
            'message': msg,
            'sticky': False,
            'type': 'info',
        }
    }

from odoo import models as _models, api as _api

class SaleOrder(_models.Model):
    _inherit = 'sale.order'

    @_api.model
    def create(self, vals):
        user = self.env.user
        plan = user.subscription_plan_id
        if plan:
            period = fields.Date.today().strftime('%Y-%m')
            usage = self.env['subscription.usage'].get_or_create_usage(user, plan, period)
            usage.sales_orders += 1
            res = super().create(vals)
            res.env.context = dict(res.env.context, subscription_notify=_subscription_notify(res, usage, plan, 'sale.order'))
            return res
        return super().create(vals)

class AccountMove(_models.Model):
    _inherit = 'account.move'

    @_api.model
    def create(self, vals):
        user = self.env.user
        plan = user.subscription_plan_id
        if plan:
            period = fields.Date.today().strftime('%Y-%m')
            usage = self.env['subscription.usage'].get_or_create_usage(user, plan, period)
            usage.invoices += 1
            res = super().create(vals)
            res.env.context = dict(res.env.context, subscription_notify=_subscription_notify(res, usage, plan, 'account.move'))
            return res
        return super().create(vals) 