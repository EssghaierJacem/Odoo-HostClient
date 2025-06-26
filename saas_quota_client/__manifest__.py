{
    "name": "SaaS Quota Client",
    "summary": "Enforce record quotas from host API",
    "version": "1.0",
    "category": "SaaS",
    "author": "Your Company",
    "depends": ["sale", "account"],
    "data": [
        "views/saas_quota_client_dashboard.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "saas_quota_client/static/src/js/saas_quota_client_dashboard.js",
        ],
    },
    "installable": True,
} 