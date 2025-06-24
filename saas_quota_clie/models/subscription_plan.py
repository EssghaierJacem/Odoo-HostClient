import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _rec_name = 'abonnement_type'

    abonnement_type = fields.Char('Abonnement Type')
    max_quotations = fields.Integer('Max Quotations')
    max_invoices = fields.Integer('Max Invoices')
    quotation_price = fields.Float('Quotation Price')
    invoice_price = fields.Float('Invoice Price')
    total_sum = fields.Float('Total Sum', compute='_compute_total_sum', store=False)

    used_quotations = fields.Integer('Quotations Used', compute='_compute_used_quotations', store=False)
    quotations_left = fields.Integer('Quotations Left', compute='_compute_used_quotations', store=False)
    used_invoices = fields.Integer('Invoices Used', compute='_compute_used_invoices', store=False)
    invoices_left = fields.Integer('Invoices Left', compute='_compute_used_invoices', store=False)

    @api.model
    def create_singleton_if_missing(self):
        plan = self.search([], limit=1)
        if not plan:
            plan = self.create({})
        return plan

    @api.model
    def default_get(self, fields):
        return super().default_get(fields)

    @api.model
    def get_or_create_singleton(self):
        plan = self.search([], limit=1)
        if not plan:
            plan = self.create({})
        return plan

    def fetch_and_update_from_host(self):
        db_name = self.env.cr.dbname
        api_url = self.env['ir.config_parameter'].sudo().get_param('saas_quota_host.api_url') or "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=10)
            data = resp.json()
            vals = {
                'abonnement_type': data.get('abonnement_type'),
                'max_quotations': data.get('max_quotations', 0),
                'max_invoices': data.get('max_invoices', 0),
                'quotation_price': data.get('quotation_price', 0.0),
                'invoice_price': data.get('invoice_price', 0.0),
                'total_sum': data.get('total_sum', 0.0),
            }
            plan = self.get_or_create_singleton()
            plan.write(vals)
        except Exception as e:
            raise UserError(_('Could not fetch subscription plan from host: %s') % str(e))

    def action_sync_from_host(self):
        self.fetch_and_update_from_host()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Subscription Plan Updated'),
                'message': _('The subscription plan has been updated from the host.'),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def cron_sync_subscription_plan(self):
        self.search([]).fetch_and_update_from_host()

    @api.depends('max_quotations', 'quotation_price', 'max_invoices', 'invoice_price')
    def _compute_total_sum(self):
        for rec in self:
            rec.total_sum = (rec.max_quotations * rec.quotation_price) + (rec.max_invoices * rec.invoice_price)

    @api.depends('max_quotations')
    def _compute_used_quotations(self):
        for rec in self:
            used = self.env['sale.order'].search_count([])
            rec.used_quotations = used
            rec.quotations_left = max(rec.max_quotations - used, 0)

    @api.depends('max_invoices')
    def _compute_used_invoices(self):
        for rec in self:
            used = self.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            rec.used_invoices = used
            rec.invoices_left = max(rec.max_invoices - used, 0) 