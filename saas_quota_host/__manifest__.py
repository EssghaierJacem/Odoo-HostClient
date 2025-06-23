{
    "name": "SaaS Quota Host",
    "summary": "Manage and expose per-client record quotas via API",
    "version": "1.0",
    "category": "SaaS",
    "author": "Your Company",
    "depends": ["base", "odoo_saas_kit"],
    "data": [
        "security/ir.model.access.csv",
        "views/saas_client_quota_views.xml",
    ],
    "installable": True,
} 