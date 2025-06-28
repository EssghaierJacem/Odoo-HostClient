from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    subscription_user_ids = fields.One2many('subscription.user', 'user_id', string='Subscriptions')
    active_subscription_id = fields.Many2one('subscription.user', string='Active Subscription', 
                                            compute='_compute_active_subscription', store=True)
    
    # Usage statistics
    total_sales_orders = fields.Integer(string='Total Sales Orders', compute='_compute_usage_stats')
    total_invoices = fields.Integer(string='Total Invoices', compute='_compute_usage_stats')
    
    @api.depends('subscription_user_ids.state')
    def _compute_active_subscription(self):
        for user in self:
            active_sub = user.subscription_user_ids.filtered(lambda s: s.state == 'active')
            user.active_subscription_id = active_sub[0] if active_sub else False
    
    @api.depends('subscription_user_ids.sales_orders_count', 'subscription_user_ids.invoices_count')
    def _compute_usage_stats(self):
        for user in self:
            user.total_sales_orders = sum(user.subscription_user_ids.mapped('sales_orders_count'))
            user.total_invoices = sum(user.subscription_user_ids.mapped('invoices_count'))
    
    def get_subscription_limits(self):
        """Get current subscription limits for the user"""
        self.ensure_one()
        if self.active_subscription_id and self.active_subscription_id.state == 'active':
            return {
                'max_sales_orders': self.active_subscription_id.plan_id.max_sales_orders,
                'max_invoices': self.active_subscription_id.plan_id.max_invoices,
                'sales_orders_used': self.active_subscription_id.sales_orders_count,
                'invoices_used': self.active_subscription_id.invoices_count,
                'sales_orders_remaining': self.active_subscription_id.sales_orders_remaining,
                'invoices_remaining': self.active_subscription_id.invoices_remaining,
            }
        return {
            'max_sales_orders': 0,
            'max_invoices': 0,
            'sales_orders_used': 0,
            'invoices_used': 0,
            'sales_orders_remaining': 0,
            'invoices_remaining': 0,
        }
    
    def can_create_sales_order(self):
        """Check if user can create a sales order"""
        self.ensure_one()
        if not self.active_subscription_id or self.active_subscription_id.state != 'active':
            return False
        return self.active_subscription_id.check_limits_and_notify('sales_order')
    
    def can_create_invoice(self):
        """Check if user can create an invoice"""
        self.ensure_one()
        if not self.active_subscription_id or self.active_subscription_id.state != 'active':
            return False
        return self.active_subscription_id.check_limits_and_notify('invoice')
    
    def action_view_subscriptions(self):
        """Action to view user's subscriptions"""
        self.ensure_one()
        return {
            'name': _('Subscriptions of %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.user',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.id)],
            'context': {'default_user_id': self.id},
        }
    
    def action_view_usage_dashboard(self):
        """Action to view usage dashboard"""
        self.ensure_one()
        return {
            'name': _('Usage Dashboard - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.dashboard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_user_id': self.id},
        } 