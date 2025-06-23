from odoo import models, fields

class SaasClientQuota(models.Model):
    _name = 'saas.client.quota'
    _description = 'SaaS Client Quota'

    client_name = fields.Char(required=True)
    db_name = fields.Char(required=True, index=True)
    max_quotations = fields.Integer(default=0)
    max_invoices = fields.Integer(default=0)

class SaasClient(models.Model):
    _inherit = 'saas.client'

    max_quotations = fields.Integer(string="Max Quotations", default=0)
    max_invoices = fields.Integer(string="Max Invoices", default=0) 