{
    'name': 'Custom Quotations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Subscription-based quotation and invoice management',
    'description': """
        Custom Quotations Module for Odoo 17
        - Subscription-based document management
        - Usage tracking for quotations and invoices
        - Real-time notifications and billing
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale_management',
        'account',
        'mail',
        'odoo_saas_kit',
        'saas_kit_custom_plans',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/usage_tracker_views.xml',
        'views/res_users_views.xml',
        'views/quotation_views.xml',
        'views/saas_plan_views.xml',
        'views/templates.xml',
        'views/assets.xml',
        'views/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}