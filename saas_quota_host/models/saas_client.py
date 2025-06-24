from odoo import models, fields, api

class SaasAbonnementType(models.Model):
    _name = 'saas.abonnement.type'
    _description = 'Abonnement Type'

    name = fields.Char('Abonnement Name', required=True, index=True)
    client_ids = fields.One2many('saas.client', 'abonnement_type_id', string='Clients')

class SaasClient(models.Model):
    _inherit = 'saas.client'

    abonnement_type_id = fields.Many2one('saas.abonnement.type', string='Abonnement Type')
    max_quotations = fields.Integer('Max Quotations', default=0)
    max_invoices = fields.Integer('Max Invoices', default=0)
    quotation_price = fields.Float('Quotation Price', default=0.0)
    invoice_price = fields.Float('Invoice Price', default=0.0)
    total_price = fields.Float('Total Price', compute='_compute_total_price', store=True)

    @api.depends('max_quotations', 'quotation_price', 'max_invoices', 'invoice_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = (rec.max_quotations * rec.quotation_price) + (rec.max_invoices * rec.invoice_price) 