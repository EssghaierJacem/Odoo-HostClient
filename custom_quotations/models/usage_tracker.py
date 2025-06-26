from odoo import models, fields, api, _
from odoo.exceptions import UserError
from decimal import Decimal, ROUND_HALF_UP

class UsageTracker(models.Model):
    _name = 'user.usage.tracker'
    _description = 'User Usage Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    subscription_type = fields.Selection([
        ('free', 'Free'),
        ('pay_per_use', 'Pay Per Use'),
        ('premium', 'Premium')
    ], string='Subscription Type', default='free', tracking=True)
    
    # Link to SaaS Plan
    saas_plan_id = fields.Many2one('saas.plan', string='SaaS Plan', tracking=True)
    subscription_fee = fields.Float(string='Subscription Fee', related='saas_plan_id.user_cost', store=True)
    
    # Usage tracking fields
    quotation_count = fields.Integer(string='Quotation Count', default=0)
    invoice_count = fields.Integer(string='Invoice Count', default=0)
    free_quotations_remaining = fields.Integer(string='Free Quotations Remaining', default=5)
    free_invoices_remaining = fields.Integer(string='Free Invoices Remaining', default=5)
    
    # Pricing fields from SaaS plan
    quotation_unit_price = fields.Float(string='Quotation Unit Price', related='saas_plan_id.quotation_unit_price', store=True)
    invoice_unit_price = fields.Float(string='Invoice Unit Price', related='saas_plan_id.invoice_unit_price', store=True)
    
    # Computed fields
    paid_quotations = fields.Integer(string='Paid Quotations', compute='_compute_paid_documents', store=True)
    paid_invoices = fields.Integer(string='Paid Invoices', compute='_compute_paid_documents', store=True)
    monthly_extra_charge = fields.Float(string='Monthly Extra Charge', compute='_compute_monthly_charges', store=True)
    total_quotation_amount = fields.Float(string='Total Quotation Amount', compute='_compute_statistics', store=True)
    total_invoice_amount = fields.Float(string='Total Invoice Amount', compute='_compute_statistics', store=True)

    @api.onchange('saas_plan_id')
    def _onchange_saas_plan(self):
        if self.saas_plan_id:
            # Update subscription type based on plan
            if self.saas_plan_id.is_premium:
                self.subscription_type = 'premium'
            elif self.saas_plan_id.is_pay_per_use:
                self.subscription_type = 'pay_per_use'
            else:
                self.subscription_type = 'free'
            
            # Update free document limits
            self.free_quotations_remaining = self.saas_plan_id.free_quotation_limit
            self.free_invoices_remaining = self.saas_plan_id.free_invoice_limit

    @api.depends('quotation_count', 'invoice_count', 'free_quotations_remaining', 'free_invoices_remaining')
    def _compute_paid_documents(self):
        for record in self:
            record.paid_quotations = max(0, record.quotation_count - (5 - record.free_quotations_remaining))
            record.paid_invoices = max(0, record.invoice_count - (5 - record.free_invoices_remaining))

    @api.depends('paid_quotations', 'paid_invoices', 'quotation_unit_price', 'invoice_unit_price', 'subscription_fee')
    def _compute_monthly_charges(self):
        for record in self:
            quotation_charges = record.paid_quotations * record.quotation_unit_price
            invoice_charges = record.paid_invoices * record.invoice_unit_price
            total_charges = quotation_charges + invoice_charges + record.subscription_fee
            record.monthly_extra_charge = float(Decimal(str(total_charges)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @api.depends('paid_quotations', 'paid_invoices', 'quotation_unit_price', 'invoice_unit_price')
    def _compute_statistics(self):
        for record in self:
            if record.subscription_type == 'pay_per_use':
                record.total_quotation_amount = float(Decimal(str(record.paid_quotations * record.quotation_unit_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                record.total_invoice_amount = float(Decimal(str(record.paid_invoices * record.invoice_unit_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            else:
                record.total_quotation_amount = 0.0
                record.total_invoice_amount = 0.0

    def update_usage(self, document_type):
        self.ensure_one()
        if document_type == 'quotation':
            if self.free_quotations_remaining > 0:
                self.free_quotations_remaining -= 1
            elif self.subscription_type == 'free':
                raise UserError(_("You have reached your free quotation limit. Please upgrade your subscription."))
            self.quotation_count += 1
        elif document_type == 'invoice':
            if self.free_invoices_remaining > 0:
                self.free_invoices_remaining -= 1
            elif self.subscription_type == 'free':
                raise UserError(_("You have reached your free invoice limit. Please upgrade your subscription."))
            self.invoice_count += 1

    def reset_monthly_charges(self):
        self.ensure_one()
        self.free_quotations_remaining = self.saas_plan_id.free_quotation_limit
        self.free_invoices_remaining = self.saas_plan_id.free_invoice_limit
        self.message_post(body=_("Monthly charges have been reset."))

    def show_usage_message(self, document_type):
        self.ensure_one()
        if self.subscription_type == 'premium':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Premium Subscription'),
                    'message': _('You have unlimited access to create documents.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        remaining = self.free_quotations_remaining if document_type == 'quotation' else self.free_invoices_remaining
        if remaining > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Free Documents Remaining'),
                    'message': _('You have %d free %s remaining.') % (remaining, document_type + 's'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        else:
            unit_price = self.quotation_unit_price if document_type == 'quotation' else self.invoice_unit_price
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Pay Per Use'),
                    'message': _('You will be charged %.2f€ for this %s.') % (unit_price, document_type),
                    'type': 'warning',
                    'sticky': False,
                }
            } 