import requests
from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        self._check_quotation_quota()
        record = super().create(vals)
        # Show notification after creation
        notification = self._get_quotation_quota_notification()
        if notification:
            self.env.context = dict(self.env.context, show_quotation_quota_notification=notification)
        return record

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

    def _get_quotation_quota_notification(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_quotations = data.get('max_quotations')
            current = self.env['sale.order'].search_count([])
            if max_quotations is not None:
                remaining = max_quotations - current
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Quota Info'),
                        'message': _('You have %d out of %d quotations left.') % (remaining, max_quotations),
                        'sticky': False,
                        'type': 'info',
                    }
                }
        except Exception:
            pass
        return None

    @api.model
    def get_quotation_quota_info(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_quotations = data.get('max_quotations')
            current = self.env['sale.order'].search_count([])
            return {
                'max_quotations': max_quotations,
                'current_quotations': current,
            }
        except Exception:
            return {
                'max_quotations': 0,
                'current_quotations': 0,
            } 