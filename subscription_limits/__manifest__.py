{
    'name': 'Subscription Limits Manager',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage subscription limits for sales orders and invoices',
    'description': """
        A comprehensive module to manage subscription limits for users.
        Features:
        - Set maximum sales orders and invoices per user
        - Dynamic subscription plans
        - Real-time notifications
        - Beautiful dashboard interface
        - Usage tracking and analytics
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'account',
        'mail',
        'web',
        'bus',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/subscription_security.xml',
        'data/subscription_data.xml',
        'views/subscription_plan_views.xml',
        'views/subscription_user_views.xml',
        'views/subscription_dashboard_views.xml',
        'views/res_users_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        # 'web.assets_backend': [
        #     'subscription_limits/static/src/js/subscription_dashboard.js',
        #     'subscription_limits/static/src/js/subscription_notifications.js',
        # ],
        # 'web.assets_frontend': [
        #     'subscription_limits/static/src/css/subscription_portal.css',
        # ],
    },
    'demo': [
        'demo/subscription_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
} 