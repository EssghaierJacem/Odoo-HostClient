/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Dialog } from "@web/core/dialog/dialog";

registry.category("services").add("subscription_notification_service", {
    start(env) {
        env.services.rpc("/user/subscription_status", {}).then((result) => {
            if (result) {
                const { remaining_free_quotations, monthly_extra_charge } = result;

                new Dialog(env, {
                    title: "Votre Abonnement",
                    body: `
                        <div style="font-size: 16px; line-height: 1.5;">
                            Il vous reste <strong>${remaining_free_quotations}</strong> devis gratuits ce mois-ci.<br/>
                            Montant dû : <strong>${monthly_extra_charge.toFixed(2)} €</strong>
                        </div>
                    `,
                    buttons: [{ text: "OK", close: true }],
                }).open();
            }
        }).catch((error) => {
            console.error("Erreur de récupération d'abonnement:", error);
        });
    },
});
