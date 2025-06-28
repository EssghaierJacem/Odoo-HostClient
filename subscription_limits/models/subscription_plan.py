from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Plan Name', required=True, translate=True)
    code = fields.Char(string='Plan Code', required=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Limits
    max_sales_orders = fields.Integer(string='Max Sales Orders', default=0, help='0 means unlimited')
    max_invoices = fields.Integer(string='Max Invoices', default=0, help='0 means unlimited')
    
    # Pricing
    price = fields.Monetary(string='Price', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    
    # Duration
    duration_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('unlimited', 'Unlimited')
    ], string='Duration Type', default='monthly', required=True)
    
    # Features
    features = fields.Text(string='Features', translate=True)
    color = fields.Char(string='Color', default='#007bff')
    icon = fields.Char(string='Icon', default='fa-star')
    
    # Related records
    subscription_user_ids = fields.One2many('subscription.user', 'plan_id', string='Subscription Users')
    
    # Statistics
    user_count = fields.Integer(string='Active Users', compute='_compute_user_count', store=True)
    total_revenue = fields.Monetary(string='Total Revenue', currency_field='currency_id', 
                                   compute='_compute_total_revenue', store=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The plan code must be unique!')
    ]
    
    @api.depends('subscription_user_ids', 'subscription_user_ids.state')
    def _compute_user_count(self):
        for plan in self:
            plan.user_count = len(plan.subscription_user_ids.filtered(lambda u: u.state == 'active'))
    
    @api.depends('subscription_user_ids', 'subscription_user_ids.total_paid')
    def _compute_total_revenue(self):
        for plan in self:
            plan.total_revenue = sum(plan.subscription_user_ids.mapped('total_paid'))
    
    @api.constrains('max_sales_orders', 'max_invoices')
    def _check_limits(self):
        for plan in self:
            if plan.max_sales_orders < 0:
                raise ValidationError(_('Maximum sales orders cannot be negative.'))
            if plan.max_invoices < 0:
                raise ValidationError(_('Maximum invoices cannot be negative.'))
    
    def name_get(self):
        result = []
        for plan in self:
            name = f"{plan.name} ({plan.code})"
            result.append((plan.id, name))
        return result
    
    def action_view_users(self):
        self.ensure_one()
        return {
            'name': _('Users of %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.user',
            'view_mode': 'tree,form',
            'domain': [('plan_id', '=', self.id)],
            'context': {'default_plan_id': self.id},
        } 