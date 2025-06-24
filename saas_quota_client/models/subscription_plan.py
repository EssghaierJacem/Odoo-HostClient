from odoo import models, fields, api

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _rec_name = 'abonnement_type'

    abonnement_type = fields.Char('Abonnement Type')
    max_quotations = fields.Integer('Max Quotations')
    max_invoices = fields.Integer('Max Invoices')
    total_owed = fields.Float('Total Owed')

    used_quotations = fields.Integer('Quotations Used', compute='_compute_used_quotations', store=False)
    quotations_left = fields.Integer('Quotations Left', compute='_compute_used_quotations', store=False)
    used_invoices = fields.Integer('Invoices Used', compute='_compute_used_invoices', store=False)
    invoices_left = fields.Integer('Invoices Left', compute='_compute_used_invoices', store=False)

    @api.model
    def update_from_api(self, api_data):
        plan = self.search([], limit=1)
        vals = {
            'abonnement_type': api_data.get('abonnement_type'),
            'max_quotations': api_data.get('max_quotations', 0),
            'max_invoices': api_data.get('max_invoices', 0),
            'total_owed': api_data.get('total_owed', 0.0),
        }
        if plan:
            plan.write(vals)
        else:
            plan = self.create(vals)
        return plan

    @api.depends('max_quotations')
    def _compute_used_quotations(self):
        for rec in self:
            used = self.env['sale.order'].search_count([])
            rec.used_quotations = used
            rec.quotations_left = max(rec.max_quotations - used, 0)

    @api.depends('max_invoices')
    def _compute_used_invoices(self):
        for rec in self:
            used = self.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            rec.used_invoices = used
            rec.invoices_left = max(rec.max_invoices - used, 0) 