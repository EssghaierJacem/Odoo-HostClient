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
        # Vérifier abonnement utilisateur
        if getattr(user, 'subscription_type', 'freemium') == 'freemium':
            count = self.search_count([('create_uid', '=', user.id)])
            if count >= 5:
                raise UserError("Limite atteinte : vous ne pouvez créer que 5 devis en mode Freemium.")

            remaining = 5 - count - 1  # -1 car on est en train d'en créer un
            res = super(CustomQuotation, self).create(vals)
            if remaining > 0:
                # Ajout d'une notification douce (context)
                res = res.with_context(flash_message=f"Attention : Il vous reste {remaining} devis disponibles.")
            return res

        return super(CustomQuotation, self).create(vals)
