from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _show_usage_message(self):
        """Show usage information message"""
        usage_tracker = self.env['user.usage.tracker'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not usage_tracker:
            return

        if usage_tracker.subscription_type == 'free':
            message = f'You have {usage_tracker.free_quotations_remaining} free quotations remaining.'
            if usage_tracker.free_quotations_remaining <= 2:
                message_type = 'warning'
            else:
                message_type = 'info'
        elif usage_tracker.subscription_type == 'pay_per_use':
            if usage_tracker.free_quotations_remaining > 0:
                message = f'You have {usage_tracker.free_quotations_remaining} free quotations remaining.'
                message_type = 'info'
            else:
                quotation_charges = usage_tracker.paid_quotations * usage_tracker.quotation_unit_price
                invoice_charges = usage_tracker.paid_invoices * usage_tracker.invoice_unit_price
                message = (
                    f'You will be charged {usage_tracker.format_amount(usage_tracker.quotation_unit_price)}€ for this quotation.\n'
                    f'Current charges: {usage_tracker.format_amount(usage_tracker.monthly_extra_charge)}€\n'
                    f'(Quotations: {usage_tracker.format_amount(quotation_charges)}€, '
                    f'Invoices: {usage_tracker.format_amount(invoice_charges)}€)'
                )
                message_type = 'warning'
        else:  # premium
            return

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Usage Information',
                'message': message,
                'type': message_type,
                'sticky': False,
            }
        }

    @api.model
    def create(self, vals):
        # Get user's usage tracker
        usage_tracker = self.env['user.usage.tracker'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not usage_tracker:
            usage_tracker = self.env['user.usage.tracker'].create({
                'user_id': self.env.user.id,
                'subscription_type': 'free'
            })

        # Update usage
        usage_tracker.update_usage('quotation')
        
        # Create notification message
        message = ''
        if usage_tracker.subscription_type == 'free':
            message = f'You have {usage_tracker.free_quotations_remaining} free quotations remaining.'
            message_type = 'warning' if usage_tracker.free_quotations_remaining <= 2 else 'info'
        elif usage_tracker.subscription_type == 'pay_per_use':
            if usage_tracker.free_quotations_remaining > 0:
                message = f'You have {usage_tracker.free_quotations_remaining} free quotations remaining.'
                message_type = 'info'
            else:
                quotation_charges = usage_tracker.paid_quotations * usage_tracker.quotation_unit_price
                invoice_charges = usage_tracker.paid_invoices * usage_tracker.invoice_unit_price
                message = (
                    f'You will be charged {usage_tracker.format_amount(usage_tracker.quotation_unit_price)}€ for this quotation.\n'
                    f'Current charges: {usage_tracker.format_amount(usage_tracker.monthly_extra_charge)}€\n'
                    f'(Quotations: {usage_tracker.format_amount(quotation_charges)}€, '
                    f'Invoices: {usage_tracker.format_amount(invoice_charges)}€)'
                )
                message_type = 'warning'
        
        if message:
            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                'simple_notification',
                {
                    'title': 'Usage Information',
                    'message': message,
                    'type': message_type
                }
            )
        
        return super(SaleOrder, self).create(vals)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Show notification when entering the view"""
        res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        notification = self._show_usage_message()
        if notification:
            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                'simple_notification',
                notification['params']
            )
        return res
