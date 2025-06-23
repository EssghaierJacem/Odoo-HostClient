import requests
from odoo import models, api, _
from odoo.exceptions import UserError
from odoo import fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        self._check_quotation_quota()
        return super().create(vals)

    def _check_quotation_quota(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_quotations = data.get('max_quotations')
            if max_quotations is not None:
                current = self.env['sale.order'].search_count([])
                if current >= max_quotations:
                    raise UserError(_("You have reached your quotation quota (%d).") % max_quotations)
        except Exception as e:
            raise UserError(_("Could not check quota: %s") % str(e))

class SaasClient(models.Model):
    _inherit = 'saas.client'

    max_quotations = fields.Integer(string="Max Quotations", default=0)
    max_invoices = fields.Integer(string="Max Invoices", default=0) 