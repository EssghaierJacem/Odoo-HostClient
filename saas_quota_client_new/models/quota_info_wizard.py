from odoo import models, fields, api, _
import requests

class QuotaInfoWizard(models.TransientModel):
    _name = 'quota.info.wizard'
    _description = 'Quota Information Wizard'

    max_quotations = fields.Integer(string="Max Quotations", readonly=True)
    current_quotations = fields.Integer(string="Current Quotations", readonly=True)
    max_invoices = fields.Integer(string="Max Invoices", readonly=True)
    current_invoices = fields.Integer(string="Current Invoices", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            res['max_quotations'] = data.get('max_quotations', 0)
            res['max_invoices'] = data.get('max_invoices', 0)
        except Exception:
            res['max_quotations'] = 0
            res['max_invoices'] = 0
        res['current_quotations'] = self.env['sale.order'].search_count([])
        res['current_invoices'] = self.env['account.move'].search_count([('move_type', 'in', ['out_invoice', 'out_refund'])])
        return res 