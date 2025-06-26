from odoo import models, fields, api
from odoo.exceptions import UserError

class CustomQuotation(models.Model):
    _name = 'custom.quotation'
    _description = 'Custom Quotation'

    name = fields.Char(string='Devis Référence', required=True)
    customer_name = fields.Char(string='Client', required=True)
    quotation_date = fields.Date(string='Date de Devis', default=fields.Date.today)
    amount_total = fields.Float(string='Montant Total')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé')
    ], string='État', default='draft')

    @api.model
    def create(self, vals):
        user = self.env.user
        today = fields.Date.today()

        # Count this month's quotations
        count = self.search_count([
            ('create_uid', '=', user.id),
            ('quotation_date', '>=', today.replace(day=1))
        ])

        if user.subscription_type == 'freemium':
            if count >= 5:
                raise UserError("Limite atteinte : vous ne pouvez créer que 5 devis en mode Freemium.")

        elif user.subscription_type == 'pay_per_use':
            if count >= 5:
                user.monthly_extra_charge += 0.30

        # Premium: No limit

        res = super(CustomQuotation, self).create(vals)

        if user.subscription_type in ['freemium', 'pay_per_use'] and count < 5:
            remaining = 5 - count - 1  # -1 because one is being created now
            if remaining > 0:
                res = res.with_context(flash_message=f"Attention : Il vous reste {remaining} devis gratuits ce mois-ci.")

        return res
