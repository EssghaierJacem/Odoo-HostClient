import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _rec_name = 'abonnement_type'

    abonnement_type = fields.Char('Abonnement Type', compute='_compute_plan', store=False, readonly=True)
    max_quotations = fields.Integer('Max Quotations', compute='_compute_plan', store=False, readonly=True)
    max_invoices = fields.Integer('Max Invoices', compute='_compute_plan', store=False, readonly=True)
    quotation_price = fields.Float('Quotation Price', compute='_compute_plan', store=False, readonly=True)
    invoice_price = fields.Float('Invoice Price', compute='_compute_plan', store=False, readonly=True)
    total_sum = fields.Float('Total Sum', compute='_compute_plan', store=False, readonly=True)

    used_quotations = fields.Integer('Quotations Used', compute='_compute_used_quotations', store=False, readonly=True)
    quotations_left = fields.Integer('Quotations Left', compute='_compute_used_quotations', store=False, readonly=True)
    used_invoices = fields.Integer('Invoices Used', compute='_compute_used_invoices', store=False, readonly=True)
    invoices_left = fields.Integer('Invoices Left', compute='_compute_used_invoices', store=False, readonly=True)

    @api.model
    def get_singleton(self):
        plan = self.search([], limit=1)
        if not plan:
            plan = self.create({})
        return plan

    @api.depends()
    def _compute_plan(self):
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=10)
            data = resp.json()
        except Exception:
            data = {}
        for rec in self:
            rec.abonnement_type = data.get('abonnement_type', '')
            rec.max_quotations = data.get('max_quotations', 0)
            rec.max_invoices = data.get('max_invoices', 0)
            rec.quotation_price = data.get('quotation_price', 0.0)
            rec.invoice_price = data.get('invoice_price', 0.0)
            rec.total_sum = data.get('total_sum', 0.0)

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

    def action_sync_from_host(self):
        """Manually sync the subscription plan from the host API and update the singleton record."""
        db_name = self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=10)
            data = resp.json()
        except Exception as e:
            raise UserError(_("Failed to sync from host: %s") % str(e))
        self.ensure_one()
        self.abonnement_type = data.get('abonnement_type', '')
        self.max_quotations = data.get('max_quotations', 0)
        self.max_invoices = data.get('max_invoices', 0)
        self.quotation_price = data.get('quotation_price', 0.0)
        self.invoice_price = data.get('invoice_price', 0.0)
        self.total_sum = data.get('total_sum', 0.0)
        return True 