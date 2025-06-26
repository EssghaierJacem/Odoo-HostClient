/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.rpc = useService("rpc");
    },

    async start() {
        await super.start();
        const result = await this.rpc('/custom_quotation/notification', {});
        if (result.message) {
            this.notification.add(result.message, {
                title: "Freemium Subscription Info",
                type: 'info',
                sticky: false,
            });
        }
    },
});
