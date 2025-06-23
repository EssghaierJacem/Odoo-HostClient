from odoo import http
from odoo.http import request
import json

class QuotaAPI(http.Controller):
    @http.route('/quota/api/v1/limits', type='http', auth='public', methods=['GET'], csrf=False)
    def get_limits(self, db_name=None, **kwargs):
        client = request.env['saas.client'].sudo().search([('database_name', '=', db_name)], limit=1)
        if not client:
            return http.Response(
                json.dumps({"error": "not found"}),
                status=404,
                content_type='application/json'
            )
        return http.Response(
            json.dumps({
                "max_quotations": client.max_quotations,
                "max_invoices": client.max_invoices
            }),
            content_type='application/json'
        ) 