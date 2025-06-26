from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    subscription_type = fields.Selection([
        ('freemium', 'Freemium'),
        ('premium', 'Premium')
    ], string="Type d'Abonnement", default='freemium')