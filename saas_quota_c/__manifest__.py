{
    "name": "SaaS Quota C",
    "summary": "Enforce record quotas from host API",
    "version": "1.0",
    "category": "SaaS",
    "author": "Your Company",
    "depends": ["sale", "account"],
    "data": [
        'security/ir.model.access.csv',
        'views/subscription_plan_views.xml',
    ],
    "installable": True,
} 