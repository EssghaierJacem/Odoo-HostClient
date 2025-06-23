from odoo import http
from odoo.http import request

class QuotaAPI(http.Controller):
    @http.route('/quota/api/v1/limits', type='http', auth='public', methods=['GET'], csrf=False)
    def get_limits(self, db_name=None, **kwargs):
        client = request.env['saas.client'].sudo().search([('db_name', '=', db_name)], limit=1)
        if not client:
            return http.Response(
                '{"error": "not found"}',
                status=404,
                content_type='application/json'
            )
        return http.Response(
            '{{"max_quotations": {}, "max_invoices": {}}}'.format(client.max_quotations, client.max_invoices),
            content_type='application/json'
        ) 