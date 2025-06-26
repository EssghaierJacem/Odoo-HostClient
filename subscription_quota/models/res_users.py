from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    subscription_plan_id = fields.Many2one('subscription.plan', string="Subscription Plan") 