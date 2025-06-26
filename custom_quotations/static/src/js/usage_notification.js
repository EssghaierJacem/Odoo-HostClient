odoo.define('custom_quotations.usage_notification', ['web.core', 'web.Widget', 'web.session', 'web.QWeb'], function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var QWeb = require('web.QWeb');

    var UsageNotification = Widget.extend({
        template: 'UsageNotification',
        events: {
            'click .o_usage_notification_close': '_onClose',
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.message = options.message;
            this.type = options.type || 'info';
        },

        start: function () {
            this.$el.html(QWeb.render('UsageNotification', {
                message: this.message
            }));
            return this._super.apply(this, arguments);
        },

        _onClose: function (ev) {
            ev.preventDefault();
            this.destroy();
        },
    });

    core.bus.on('usage_notification', this, function (data) {
        var notification = new UsageNotification(this, {
            message: data.message,
            type: data.type,
        });
        notification.appendTo($('body'));
    });

    return UsageNotification;
}); 