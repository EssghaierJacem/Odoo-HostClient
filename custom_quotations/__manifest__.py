{
    'name': 'Custom Quotations',
    'version': '1.0',
    'summary': 'Module pour gérer les devis personnalisés',
    'description': 'Un module simple pour gérer les devis',
    'category': 'Sales',
    'author': 'Ton Nom',
    'depends': [
        'base',
        'sale_management',
        'web',],
    'data': [
        'security/ir.model.access.csv',
        'views/quotation_views.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/custom_quotations/static/src/js/custom_quotation_notification.js',
        ],
    },
    'import': [
        'controllers',
    ],
    'installable': True,
    'application': True,
}