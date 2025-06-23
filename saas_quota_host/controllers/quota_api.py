from odoo import http
from odoo.http import request

class QuotaAPI(http.Controller):
    @http.route('/quota/api/v1/limits', type='json', auth='public', methods=['GET'], csrf=False)
    def get_limits(self, db_name=None, **kwargs):
        quota = request.env['saas.client.quota'].sudo().search([('db_name', '=', db_name)], limit=1)
        if not quota:
            return {'error': 'not found'}
        return {
            'max_quotations': quota.max_quotations,
            'max_invoices': quota.max_invoices,
        } 