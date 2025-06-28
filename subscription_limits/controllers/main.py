from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class SubscriptionLimitsController(http.Controller):

    @http.route('/subscription/dashboard', type='http', auth='user', website=True)
    def subscription_dashboard(self, **kwargs):
        """Main dashboard page"""
        user = request.env.user
        subscription = user.active_subscription_id
        
        if not subscription:
            return request.render('subscription_limits.no_subscription_template', {
                'user': user,
            })
        
        # Get usage data
        usage_data = {
            'sales_orders': {
                'used': subscription.sales_orders_count,
                'max': subscription.plan_id.max_sales_orders,
                'remaining': subscription.sales_orders_remaining,
                'percentage': (subscription.sales_orders_count / subscription.plan_id.max_sales_orders * 100) if subscription.plan_id.max_sales_orders > 0 else 0
            },
            'invoices': {
                'used': subscription.invoices_count,
                'max': subscription.plan_id.max_invoices,
                'remaining': subscription.invoices_remaining,
                'percentage': (subscription.invoices_count / subscription.plan_id.max_invoices * 100) if subscription.plan_id.max_invoices > 0 else 0
            }
        }
        
        return request.render('subscription_limits.dashboard_template', {
            'user': user,
            'subscription': subscription,
            'usage_data': usage_data,
        })

    @http.route('/subscription/api/usage', type='json', auth='user')
    def get_usage_data(self):
        """API endpoint to get current usage data"""
        user = request.env.user
        subscription = user.active_subscription_id
        
        if not subscription:
            return {
                'error': 'No active subscription found',
                'has_subscription': False
            }
        
        return {
            'has_subscription': True,
            'subscription': {
                'name': subscription.plan_id.name,
                'state': subscription.state,
                'start_date': subscription.start_date.strftime('%Y-%m-%d') if subscription.start_date else None,
                'end_date': subscription.end_date.strftime('%Y-%m-%d') if subscription.end_date else None,
            },
            'usage': {
                'sales_orders': {
                    'used': subscription.sales_orders_count,
                    'max': subscription.plan_id.max_sales_orders,
                    'remaining': subscription.sales_orders_remaining,
                    'percentage': (subscription.sales_orders_count / subscription.plan_id.max_sales_orders * 100) if subscription.plan_id.max_sales_orders > 0 else 0
                },
                'invoices': {
                    'used': subscription.invoices_count,
                    'max': subscription.plan_id.max_invoices,
                    'remaining': subscription.invoices_remaining,
                    'percentage': (subscription.invoices_count / subscription.plan_id.max_invoices * 100) if subscription.plan_id.max_invoices > 0 else 0
                }
            }
        }

    @http.route('/subscription/api/plans', type='json', auth='user')
    def get_available_plans(self):
        """API endpoint to get available subscription plans"""
        plans = request.env['subscription.plan'].search([('active', '=', True)])
        
        return {
            'plans': [{
                'id': plan.id,
                'name': plan.name,
                'code': plan.code,
                'description': plan.description,
                'price': plan.price,
                'currency': plan.currency_id.name,
                'max_sales_orders': plan.max_sales_orders,
                'max_invoices': plan.max_invoices,
                'duration_type': plan.duration_type,
                'features': plan.features,
                'color': plan.color,
                'icon': plan.icon,
            } for plan in plans]
        }

    @http.route('/subscription/api/upgrade', type='json', auth='user')
    def upgrade_subscription(self, plan_id):
        """API endpoint to upgrade subscription"""
        user = request.env.user
        plan = request.env['subscription.plan'].browse(int(plan_id))
        
        if not plan.exists():
            return {'error': 'Plan not found'}
        
        # Create new subscription
        subscription = request.env['subscription.user'].create({
            'user_id': user.id,
            'plan_id': plan.id,
            'state': 'draft',
        })
        
        return {
            'success': True,
            'subscription_id': subscription.id,
            'message': f'Subscription to {plan.name} created successfully'
        }

    @http.route('/subscription/api/activate', type='json', auth='user')
    def activate_subscription(self, subscription_id):
        """API endpoint to activate subscription"""
        subscription = request.env['subscription.user'].browse(int(subscription_id))
        
        if not subscription.exists() or subscription.user_id != request.env.user:
            return {'error': 'Subscription not found or access denied'}
        
        subscription.action_activate()
        
        return {
            'success': True,
            'message': 'Subscription activated successfully'
        } 