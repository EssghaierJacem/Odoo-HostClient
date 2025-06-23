from odoo import http
from odoo.http import request

class QuotaAPI(http.Controller):
    @http.route('/quota/api/v1/limits', type='json', auth='public', methods=['GET'], csrf=False)
    def get_limits(self, db_name=None, **kwargs):
        client = request.env['saas.client'].sudo().search([('db_name', '=', db_name)], limit=1)
        if not client:
            return {'error': 'not found'}
        return {
            'max_quotations': client.max_quotations,
            'max_invoices': client.max_invoices,
        } 