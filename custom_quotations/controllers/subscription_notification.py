from odoo import http
from odoo.http import request

class SubscriptionNotification(http.Controller):

    @http.route('/custom_quotation/notification', type='json', auth='user')
    def subscription_notification(self):
        user = request.env.user
        if user.subscription_type == 'freemium':
            quotation_count = request.env['sale.order'].search_count([
                ('create_uid', '=', user.id),
                ('state', 'in', ['draft', 'sent'])
            ])
            remaining = max(0, 5 - quotation_count)
            message = f"Bienvenue {user.name} ! Il vous reste {remaining} devis disponibles."
            return {'message': message}
        return {'message': False}
