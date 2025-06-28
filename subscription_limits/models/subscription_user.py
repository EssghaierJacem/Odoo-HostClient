from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SubscriptionUser(models.Model):
    _name = 'subscription.user'
    _description = 'Subscription User'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Subscription Name', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', related='user_id.partner_id', store=True)
    plan_id = fields.Many2one('subscription.plan', string='Subscription Plan', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date(string='End Date', compute='_compute_end_date', store=True)
    last_renewal_date = fields.Date(string='Last Renewal Date')
    
    # Usage tracking
    sales_orders_count = fields.Integer(string='Sales Orders Used', compute='_compute_usage', store=True)
    invoices_count = fields.Integer(string='Invoices Used', compute='_compute_usage', store=True)
    sales_orders_remaining = fields.Integer(string='Sales Orders Remaining', compute='_compute_remaining', store=True)
    invoices_remaining = fields.Integer(string='Invoices Remaining', compute='_compute_remaining', store=True)
    
    # Plan limits (computed for view access)
    plan_max_sales_orders = fields.Integer(string='Plan Max Sales Orders', compute='_compute_plan_limits', store=True)
    plan_max_invoices = fields.Integer(string='Plan Max Invoices', compute='_compute_plan_limits', store=True)
    
    # Financial
    total_paid = fields.Monetary(string='Total Paid', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 related='plan_id.currency_id', store=True)
    
    # Related records
    sale_order_ids = fields.One2many('sale.order', 'subscription_user_id', string='Sales Orders')
    invoice_ids = fields.One2many('account.move', 'subscription_user_id', string='Invoices')
    
    # Notifications
    notification_sent = fields.Boolean(string='Warning Sent', default=False)
    
    def unlink(self):
        for rec in self:
            log_count = self.env['subscription.usage.log'].search_count([('subscription_id', '=', rec.id)])
            if log_count:
                raise UserError(_("You cannot delete a subscription user with usage logs. Please archive the record instead."))
        return super().unlink()
    
    @api.depends('user_id', 'plan_id')
    def _compute_name(self):
        for record in self:
            if record.user_id and record.plan_id:
                record.name = f"{record.user_id.name} - {record.plan_id.name}"
            elif record.user_id:
                record.name = f"{record.user_id.name} - Subscription"
            elif record.plan_id:
                record.name = f"Subscription - {record.plan_id.name}"
            else:
                record.name = "Subscription"
    
    @api.depends('start_date', 'plan_id.duration_type')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.plan_id:
                if record.plan_id.duration_type == 'monthly':
                    record.end_date = record.start_date + timedelta(days=30)
                elif record.plan_id.duration_type == 'quarterly':
                    record.end_date = record.start_date + timedelta(days=90)
                elif record.plan_id.duration_type == 'yearly':
                    record.end_date = record.start_date + timedelta(days=365)
                else:  # unlimited
                    record.end_date = False
            else:
                record.end_date = False
    
    @api.depends('user_id', 'plan_id')
    def _compute_usage(self):
        for record in self:
            # Count usage logs for this subscription
            record.sales_orders_count = self.env['subscription.usage.log'].search_count([
                ('subscription_id', '=', record.id),
                ('record_type', '=', 'sales_order')
            ])
            record.invoices_count = self.env['subscription.usage.log'].search_count([
                ('subscription_id', '=', record.id),
                ('record_type', '=', 'invoice')
            ])
            _logger.info(f"[DEBUG] Subscription {record.id}: sales_orders_count={record.sales_orders_count}, invoices_count={record.invoices_count}")
    
    @api.depends('sales_orders_count', 'invoices_count', 'plan_id.max_sales_orders', 'plan_id.max_invoices')
    def _compute_remaining(self):
        for record in self:
            if record.plan_id.max_sales_orders > 0:
                record.sales_orders_remaining = max(0, record.plan_id.max_sales_orders - record.sales_orders_count)
            else:
                record.sales_orders_remaining = -1  # Unlimited
            _logger.info(f"[DEBUG] Subscription {record.id}: max_sales_orders={record.plan_id.max_sales_orders}, sales_orders_count={record.sales_orders_count}, sales_orders_remaining={record.sales_orders_remaining}")
            
            if record.plan_id.max_invoices > 0:
                record.invoices_remaining = max(0, record.plan_id.max_invoices - record.invoices_count)
            else:
                record.invoices_remaining = -1  # Unlimited
    
    @api.constrains('user_id', 'plan_id', 'state')
    def _check_unique_active_subscription(self):
        for record in self:
            if record.state == 'active':
                existing = self.search([
                    ('user_id', '=', record.user_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('User %s already has an active subscription.') % record.user_id.name)
    
    def action_activate(self):
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'active'
            self.last_renewal_date = fields.Date.today()
            self._send_activation_notification()
    
    def action_suspend(self):
        self.ensure_one()
        if self.state == 'active':
            self.state = 'suspended'
            self._send_suspension_notification()
    
    def action_cancel(self):
        self.ensure_one()
        if self.state in ['active', 'suspended']:
            self.state = 'cancelled'
            self._send_cancellation_notification()
    
    def action_renew(self):
        self.ensure_one()
        if self.state in ['active', 'expired']:
            self.start_date = fields.Date.today()
            self.last_renewal_date = fields.Date.today()
            self.state = 'active'
            self.notification_sent = False
            self._send_renewal_notification()
    
    def _send_activation_notification(self):
        self.ensure_one()
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'success',
                'title': _('Subscription Activated'),
                'message': _('Your subscription to %s has been activated successfully!') % self.plan_id.name
            }
        )
    
    def _send_suspension_notification(self):
        self.ensure_one()
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'warning',
                'title': _('Subscription Suspended'),
                'message': _('Your subscription to %s has been suspended.') % self.plan_id.name
            }
        )
    
    def _send_cancellation_notification(self):
        self.ensure_one()
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'danger',
                'title': _('Subscription Cancelled'),
                'message': _('Your subscription to %s has been cancelled.') % self.plan_id.name
            }
        )
    
    def _send_renewal_notification(self):
        self.ensure_one()
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'success',
                'title': _('Subscription Renewed'),
                'message': _('Your subscription to %s has been renewed successfully!') % self.plan_id.name
            }
        )
    
    def check_limits_and_notify(self, record_type='sales_order'):
        self.ensure_one()
        
        if record_type == 'sales_order':
            remaining = self.sales_orders_remaining
            limit_reached = remaining == 0
        else:  # invoice
            remaining = self.invoices_remaining
            limit_reached = remaining == 0
        
        if limit_reached:
            self._send_limit_reached_notification(record_type)
            return False
        elif remaining <= 2 and not self.notification_sent:  # Warning when 2 or fewer remaining
            self._send_warning_notification(record_type, remaining)
            self.notification_sent = True
            return True
        else:
            return True
    
    def _send_warning_notification(self, record_type, remaining):
        self.ensure_one()
        record_type_name = 'sales orders' if record_type == 'sales_order' else 'invoices'
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'warning',
                'title': _('Subscription Limit Warning'),
                'message': _('You have only %d %s remaining in your subscription.') % (remaining, record_type_name)
            }
        )
    
    def _send_limit_reached_notification(self, record_type):
        self.ensure_one()
        record_type_name = 'sales orders' if record_type == 'sales_order' else 'invoices'
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'danger',
                'title': _('Subscription Limit Reached'),
                'message': _('You have reached your limit for %s. Please upgrade your subscription.') % record_type_name
            }
        )
    
    @api.model
    def _migrate_usage_logs_record_type(self):
        """Migrate existing usage logs to set record_type field"""
        logs = self.env['subscription.usage.log'].search([('record_type', '=', False)])
        for log in logs:
            if log.sale_order_id:
                log.record_type = 'sales_order'
            elif log.invoice_id:
                log.record_type = 'invoice'
            else:
                # If neither is set, default to sales_order (or delete if invalid)
                log.record_type = 'sales_order'
        _logger.info(f"Migrated {len(logs)} usage log records")
    
    @api.model
    def _cron_check_expired_subscriptions(self):
        """Cron job to check and expire subscriptions"""
        expired_subscriptions = self.search([
            ('state', '=', 'active'),
            ('end_date', '<', fields.Date.today()),
            ('end_date', '!=', False)
        ])
        
        for subscription in expired_subscriptions:
            subscription.state = 'expired'
            subscription._send_expiration_notification()
    
    def _send_expiration_notification(self):
        self.ensure_one()
        self.env['bus.bus']._sendone(
            self.user_id.partner_id,
            'simple_notification',
            {
                'type': 'warning',
                'title': _('Subscription Expired'),
                'message': _('Your subscription to %s has expired. Please renew to continue using the service.') % self.plan_id.name
            }
        )
    
    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if not record.name or record.name.strip() == '':
                raise ValidationError(_('Subscription name cannot be empty.'))

    @api.depends('plan_id.max_sales_orders', 'plan_id.max_invoices')
    def _compute_plan_limits(self):
        for record in self:
            record.plan_max_sales_orders = record.plan_id.max_sales_orders if record.plan_id else 0
            record.plan_max_invoices = record.plan_id.max_invoices if record.plan_id else 0

    @api.model
    def create(self, vals):
        _logger.info(f"[DEBUG] SubscriptionUser.create called with vals: {vals}")
        record = super().create(vals)
        if vals.get('state') == 'active':
            _logger.info(f"[DEBUG] Creating activation log for subscription {record.id}")
            record._create_activation_log()
        return record

    def write(self, vals):
        _logger.info(f"[DEBUG] SubscriptionUser.write called with vals: {vals} for ids: {self.ids}")
        res = super().write(vals)
        for rec in self:
            if 'state' in vals and vals['state'] == 'active':
                _logger.info(f"[DEBUG] Creating activation log for subscription {rec.id} in write")
                rec._create_activation_log()
        return res

    def _create_activation_log(self):
        _logger.info(f"[DEBUG] _create_activation_log called for subscription {self.id}")
        UsageLog = self.env['subscription.usage.log']
        if not UsageLog.search([('subscription_id', '=', self.id), ('record_type', '=', 'activation')]):
            UsageLog.create({
                'user_id': self.user_id.id,
                'subscription_id': self.id,
                'record_type': 'activation',
            })
            _logger.info(f"[DEBUG] Activation log created for subscription {self.id}")
        else:
            _logger.info(f"[DEBUG] Activation log already exists for subscription {self.id}")


class SubscriptionUsageLog(models.Model):
    _name = 'subscription.usage.log'
    _description = 'Subscription Usage Log'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', string='User', required=True)
    subscription_id = fields.Many2one('subscription.user', string='Subscription', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    record_type = fields.Selection([
        ('sales_order', 'Sales Order'),
        ('invoice', 'Invoice'),
        ('activation', 'Activation'),
    ], string='Record Type')
    
    # Computed fields for easy access
    record_name = fields.Char(string='Record Name', compute='_compute_record_name', store=True)
    record_number = fields.Char(string='Record Number', compute='_compute_record_name', store=True)
    
    @api.depends('sale_order_id', 'invoice_id', 'record_type')
    def _compute_record_name(self):
        for record in self:
            if record.record_type == 'sales_order' and record.sale_order_id:
                record.record_name = record.sale_order_id.name
                record.record_number = record.sale_order_id.name
            elif record.record_type == 'invoice' and record.invoice_id:
                record.record_name = record.invoice_id.name
                record.record_number = record.invoice_id.name
            else:
                record.record_name = ''
                record.record_number = ''
    
    @api.constrains('sale_order_id', 'invoice_id', 'record_type')
    def _check_record_consistency(self):
        for record in self:
            if record.record_type == 'sales_order' and not record.sale_order_id:
                raise ValidationError(_('Sales Order must be specified for sales order records.'))
            elif record.record_type == 'invoice' and not record.invoice_id:
                raise ValidationError(_('Invoice must be specified for invoice records.'))
            elif record.record_type == 'sales_order' and record.invoice_id:
                raise ValidationError(_('Invoice should not be specified for sales order records.'))
            elif record.record_type == 'invoice' and record.sale_order_id:
                raise ValidationError(_('Sales Order should not be specified for invoice records.'))
            # Allow empty record_type during migration 