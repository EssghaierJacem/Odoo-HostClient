from odoo import models, fields

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'

    name = fields.Char(required=True)
    base_price = fields.Float(string="Base Price", required=True)
    free_sales_orders = fields.Integer(string="Free Sales Orders", default=0)
    free_invoices = fields.Integer(string="Free Invoices", default=0)
    price_per_extra_so = fields.Float(string="Price per Extra Sales Order", default=0.0)
    price_per_extra_invoice = fields.Float(string="Price per Extra Invoice", default=0.0)
    active = fields.Boolean(default=True) 