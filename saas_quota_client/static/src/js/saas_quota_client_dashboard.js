odoo.define('saas_quota_client.dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Notification = require('web.Notification');

    var Dashboard = AbstractAction.extend({
        template: 'saas_quota_client_dashboard_template',
        start: function () {
            var self = this;
            // Fetch quota info from the backend
            var quotationPromise = rpc.query({
                model: 'sale.order',
                method: 'get_quotation_quota_info',
                args: [],
            });
            var invoicePromise = rpc.query({
                model: 'account.move',
                method: 'get_invoice_quota_info',
                args: [],
            });
            Promise.all([quotationPromise, invoicePromise]).then(function(results) {
                var q = results[0];
                var i = results[1];
                var msg = _.str.sprintf('You have %s out of %s quotations left. You have %s out of %s invoices left.',
                    q.max_quotations - q.current_quotations,
                    q.max_quotations,
                    i.max_invoices - i.current_invoices,
                    i.max_invoices
                );
                self.displayNotification({
                    title: 'Quota Info',
                    message: msg,
                    type: 'info',
                    sticky: true
                });
            }).catch(function () {
                self.displayNotification({
                    title: 'Quota Info',
                    message: 'Could not fetch quota information.',
                    type: 'danger',
                    sticky: true
                });
            });
            return this._super.apply(this, arguments);
        },
    });

    core.action_registry.add('saas_quota_client_dashboard', Dashboard);

    return Dashboard;
}); 