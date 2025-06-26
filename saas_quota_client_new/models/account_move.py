import requests
from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        self._check_invoice_quota()
        record = super().create(vals)
        # Show notification after creation
        notification = self._get_invoice_quota_notification()
        if notification:
            self.env.context = dict(self.env.context, show_invoice_quota_notification=notification)
        return record

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

    def _get_invoice_quota_notification(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_invoices = data.get('max_invoices')
            current = self.env['account.move'].search_count([('move_type', 'in', ['out_invoice', 'out_refund'])])
            if max_invoices is not None:
                remaining = max_invoices - current
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Quota Info'),
                        'message': _('You have %d out of %d invoices left.') % (remaining, max_invoices),
                        'sticky': False,
                        'type': 'info',
                    }
                }
        except Exception:
            pass
        return None

    @api.model
    def get_invoice_quota_info(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=5)
            data = resp.json()
            max_invoices = data.get('max_invoices')
            current = self.env['account.move'].search_count([('move_type', 'in', ['out_invoice', 'out_refund'])])
            return {
                'max_invoices': max_invoices,
                'current_invoices': current,
            }
        except Exception:
            return {
                'max_invoices': 0,
                'current_invoices': 0,
            } 