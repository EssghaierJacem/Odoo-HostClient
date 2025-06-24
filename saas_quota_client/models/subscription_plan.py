from odoo import models, fields, api

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _rec_name = 'abonnement_type'

    abonnement_type = fields.Char('Abonnement Type')
    max_quotations = fields.Integer('Max Quotations')
    used_quotations = fields.Integer('Quotations Used')
    max_invoices = fields.Integer('Max Invoices')
    used_invoices = fields.Integer('Invoices Used')
    total_owed = fields.Float('Total Owed')

    @api.model
    def update_from_api(self, api_data):
        plan = self.search([], limit=1)
        vals = {
            'abonnement_type': api_data.get('abonnement_type'),
            'max_quotations': api_data.get('max_quotations', 0),
            'used_quotations': api_data.get('used_quotations', 0),
            'max_invoices': api_data.get('max_invoices', 0),
            'used_invoices': api_data.get('used_invoices', 0),
            'total_owed': api_data.get('total_owed', 0.0),
        }
        if plan:
            plan.write(vals)
        else:
            plan = self.create(vals)
        return plan 