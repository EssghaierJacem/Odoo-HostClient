import requests
from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        self._check_invoice_quota()
        return super().create(vals)

    def _check_invoice_quota(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_invoices = data.get('max_invoices')
            if max_invoices is not None:
                current = self.env['account.move'].search_count([('move_type', 'in', ['out_invoice', 'out_refund'])])
                if current >= max_invoices:
                    raise UserError(_("You have reached your invoice quota (%d).") % max_invoices)
        except Exception as e:
            raise UserError(_("Could not check quota: %s") % str(e)) 