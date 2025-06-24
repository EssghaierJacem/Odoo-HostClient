import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'
    _rec_name = 'abonnement_type'

    abonnement_type = fields.Char('Abonnement Type', readonly=True)
    max_quotations = fields.Integer('Max Quotations', readonly=True)
    max_invoices = fields.Integer('Max Invoices', readonly=True)
    quotation_price = fields.Float('Quotation Price', readonly=True)
    invoice_price = fields.Float('Invoice Price', readonly=True)
    total_sum = fields.Float('Total Sum', readonly=True)

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

    def action_fetch_from_host(self):
        IrConfig = self.env['ir.config_parameter'].sudo()
        db_name = IrConfig.get_param('saas_quota_client.db_name') or self.env.cr.dbname
        api_url = "https://www.yonnovia.xyz/quota/api/v1/limits"
        try:
            resp = requests.get(f"{api_url}?db_name={db_name}", timeout=10)
            data = resp.json()
        except Exception as e:
            raise UserError(_("Failed to fetch from host: %s") % str(e))
        plan = self
        if not plan:
            plan = self.create({})
        plan.write({
            'abonnement_type': data.get('abonnement_type', ''),
            'max_quotations': data.get('max_quotations', 0),
            'max_invoices': data.get('max_invoices', 0),
            'quotation_price': data.get('quotation_price', 0.0),
            'invoice_price': data.get('invoice_price', 0.0),
            'total_sum': data.get('total_sum', 0.0),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Quota Fetched'),
                'message': _('Subscription plan updated from host.'),
                'type': 'success',
                'sticky': False,
            }
        }

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

    def unlink(self):
        raise UserError(_('You cannot delete the subscription plan.'))

    def write(self, vals):
        # Prevent manual editing except via the sync button
        if self.env.context.get('from_sync_button'):
            return super().write(vals)
        raise UserError(_('You cannot edit the subscription plan manually.'))

    @api.model_create_multi
    def create(self, vals_list):
        if self.search_count([]) > 0:
            raise UserError(_('Only one subscription plan record is allowed.'))
        return super().create(vals_list) 