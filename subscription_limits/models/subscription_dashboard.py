from odoo import models, fields, api, _

class SubscriptionDashboard(models.TransientModel):
    _name = 'subscription.dashboard'
    _description = 'Subscription Dashboard'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    subscription = fields.Many2one('subscription.user', string='Active Subscription', 
                                  related='user_id.active_subscription_id', readonly=True)
    
    # Computed fields for view access
    subscription_plan_name = fields.Char(string='Plan Name', compute='_compute_subscription_data')
    subscription_state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', compute='_compute_subscription_data')
    subscription_start_date = fields.Date(string='Start Date', compute='_compute_subscription_data')
    subscription_end_date = fields.Date(string='End Date', compute='_compute_subscription_data')
    subscription_sales_orders_count = fields.Integer(string='Sales Orders Used', compute='_compute_subscription_data')
    subscription_invoices_count = fields.Integer(string='Invoices Used', compute='_compute_subscription_data')
    subscription_sales_orders_remaining = fields.Integer(string='Sales Orders Remaining', compute='_compute_subscription_data')
    subscription_invoices_remaining = fields.Integer(string='Invoices Remaining', compute='_compute_subscription_data')
    subscription_plan_max_sales_orders = fields.Integer(string='Plan Max Sales Orders', compute='_compute_subscription_data')
    subscription_plan_max_invoices = fields.Integer(string='Plan Max Invoices', compute='_compute_subscription_data')
    
    @api.depends('subscription')
    def _compute_subscription_data(self):
        for record in self:
            if record.subscription:
                record.subscription_plan_name = record.subscription.plan_id.name
                record.subscription_state = record.subscription.state
                record.subscription_start_date = record.subscription.start_date
                record.subscription_end_date = record.subscription.end_date
                record.subscription_sales_orders_count = record.subscription.sales_orders_count
                record.subscription_invoices_count = record.subscription.invoices_count
                record.subscription_sales_orders_remaining = record.subscription.sales_orders_remaining
                record.subscription_invoices_remaining = record.subscription.invoices_remaining
                record.subscription_plan_max_sales_orders = record.subscription.plan_max_sales_orders
                record.subscription_plan_max_invoices = record.subscription.plan_max_invoices
            else:
                record.subscription_plan_name = False
                record.subscription_state = False
                record.subscription_start_date = False
                record.subscription_end_date = False
                record.subscription_sales_orders_count = 0
                record.subscription_invoices_count = 0
                record.subscription_sales_orders_remaining = 0
                record.subscription_invoices_remaining = 0
                record.subscription_plan_max_sales_orders = 0
                record.subscription_plan_max_invoices = 0
    
    def action_view_subscriptions(self):
        """Action to view user's subscriptions"""
        return {
            'name': _('My Subscriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.user',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'context': {'default_user_id': self.user_id.id},
        }
    
    def action_view_plans(self):
        """Action to view available plans"""
        return {
            'name': _('Available Plans'),
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.plan',
            'view_mode': 'kanban,tree,form',
            'context': {'search_default_active': 1},
        }
    
    def action_view_usage_report(self):
        """Action to view usage report"""
        return {
            'name': _('Usage Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.user',
            'view_mode': 'form',
            'res_id': self.subscription.id if self.subscription else False,
            'target': 'new',
        } 