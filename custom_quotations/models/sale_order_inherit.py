from odoo import models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        user = self.env.user
        # Vérifier abonnement utilisateur
        if getattr(user, 'subscription_type', 'freemium') == 'freemium':
            count = self.search_count([('create_uid', '=', user.id)])
            if count >= 5:
                raise UserError("Limite atteinte : vous ne pouvez créer que 5 devis en mode Freemium.")

            remaining = 5 - count - 1  # -1 car on est en train d'en créer un
            res = super(SaleOrder, self).create(vals)
            if remaining > 0:
                res = res.with_context(flash_message=f"Attention : Il vous reste {remaining} devis disponibles.")
            return res

        return super(SaleOrder, self).create(vals)
