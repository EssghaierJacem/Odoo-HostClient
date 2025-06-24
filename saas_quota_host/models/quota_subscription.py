from odoo import models, fields, api

class SaasQuotaSubscription(models.Model):
    _name = 'saas.quota.subscription'
    _description = 'SaaS Quota Subscription'

    name = fields.Char('Subscription Name', required=True)
    max_quotations = fields.Integer('Max Quotations', default=0)
    max_invoices = fields.Integer('Max Invoices', default=0)
    quotation_price = fields.Float('Quotation Price', default=0.0)
    invoice_price = fields.Float('Invoice Price', default=0.0)
    total_price = fields.Float('Total Price', compute='_compute_total_price', store=True)
    used_quotations = fields.Integer('Used Quotations', default=0)
    used_invoices = fields.Integer('Used Invoices', default=0)

    @api.depends('quotation_price', 'invoice_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.quotation_price + rec.invoice_price

    def action_reset_usage(self):
        for rec in self:
            rec.used_quotations = 0
            rec.used_invoices = 0 