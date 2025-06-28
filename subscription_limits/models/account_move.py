from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_user_id = fields.Many2one('subscription.user', string='Subscription User', 
                                          related='user_id.active_subscription_id', store=True)
    
    @api.model
    def create(self, vals):
        """Override create to check subscription limits for invoices"""
        user = self.env.user
        move_type = vals.get('move_type', '')
        
        # Only check for customer invoices
        if move_type == 'out_invoice':
            if not user.can_create_invoice():
                raise UserError(_('You have reached your invoice limit or your subscription is not active. Please upgrade your subscription to create more invoices.'))
        
        invoice = super().create(vals)
        return invoice
    
    def action_post(self):
        """Override action_post to check limits before posting"""
        for move in self:
            if move.move_type == 'out_invoice' and move.subscription_user_id and move.subscription_user_id.state == 'active':
                if not move.subscription_user_id.check_limits_and_notify('invoice'):
                    raise UserError(_('Cannot post invoice. You have reached your subscription limit for invoices.'))
        
        res = super().action_post()
        for invoice in self:
            # Try to get the subscription from the invoice, or fallback to the user's active subscription
            subscription = invoice.subscription_user_id or invoice.user_id.active_subscription_id
            if subscription:
                UsageLog = self.env['subscription.usage.log']
                if not UsageLog.search([('invoice_id', '=', invoice.id)]):
                    UsageLog.create({
                        'user_id': subscription.user_id.id,
                        'subscription_id': subscription.id,
                        'invoice_id': invoice.id,
                        'record_type': 'invoice',
                    })
                    # Force recompute after log creation
                    subscription._compute_usage()
                    subscription._compute_remaining()
                remaining = subscription.invoices_remaining
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Subscription Usage',
                        'message': f'You have {remaining if remaining >= 0 else "unlimited"} invoices left.',
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