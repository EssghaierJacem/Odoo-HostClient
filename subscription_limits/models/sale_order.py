from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subscription_user_id = fields.Many2one('subscription.user', string='Subscription User', 
                                          related='user_id.active_subscription_id', store=True)
    
    @api.model
    def create(self, vals):
        """Override create to check subscription limits"""
        user = self.env.user
        if not user.can_create_sales_order():
            raise UserError(_('You have reached your sales order limit or your subscription is not active. Please upgrade your subscription to create more sales orders.'))
        
        order = super().create(vals)
        return order
    
    def action_confirm(self):
        """Override action_confirm to check limits before confirming"""
        for order in self:
            if order.subscription_user_id and order.subscription_user_id.state == 'active':
                if not order.subscription_user_id.check_limits_and_notify('sales_order'):
                    raise UserError(_('Cannot confirm sales order. You have reached your subscription limit for sales orders.'))
        
        res = super().action_confirm()
        
        # Log usage for all confirmed orders
        for order in self:
            # Try to get the subscription from the order, or fallback to the user's active subscription
            subscription = order.subscription_user_id or order.user_id.active_subscription_id
            if not subscription:
                raise UserError("You must assign a subscription to this sales order before confirming.")
            
            # Create usage log if it doesn't exist
            UsageLog = self.env['subscription.usage.log']
            if not UsageLog.search([('sale_order_id', '=', order.id)]):
                UsageLog.create({
                    'user_id': subscription.user_id.id,
                    'subscription_id': subscription.id,
                    'sale_order_id': order.id,
                    'record_type': 'sales_order',
                })
                # Force recompute after log creation
                subscription._compute_usage()
                subscription._compute_remaining()
        
        # Return notification only once (for the first order)
        if self:
            subscription = self[0].subscription_user_id or self[0].user_id.active_subscription_id
            if subscription:
                # Use the updated value
                remaining = subscription.sales_orders_remaining
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Subscription Usage',
                        'message': f'You have {remaining if remaining >= 0 else "unlimited"} sales orders left.',
                        'type': 'info',
                        'sticky': False,
                    }
                }
        
        return res
    
    def action_view_subscription(self):
        """Action to view related subscription"""
        self.ensure_one()
        if self.subscription_user_id:
            return {
                'name': _('Subscription Details'),
                'type': 'ir.actions.act_window',
                'res_model': 'subscription.user',
                'view_mode': 'form',
                'res_id': self.subscription_user_id.id,
                'target': 'new',
            }
        return False

    def unlink(self):
        for order in self:
            if order.state in ['sale', 'done']:
                raise UserError("You cannot delete a confirmed sales order. Please cancel it first.")
        return super().unlink()

    def action_cancel(self):
        res = super().action_cancel()
        return res 