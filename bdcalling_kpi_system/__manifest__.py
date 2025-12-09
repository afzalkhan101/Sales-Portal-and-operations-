{
    'name': "KPI Bonus System",
    'version': '1.0.0',
    'summary': "Manage KPI and Bonus System for Bdcalling Sales Portal",
    'description': """
    """,
    'author': "Afzal Khan",
    'website': "https://www.example.com",
    'category': 'Bdcalling Portal',
    'depends': [
        'base',
        'mail',
        'sale',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_config_views.xml',
        'views/hremployee_views.xml',
        'views/sales_kpi_views.xml',
        'views/operations_kpi.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
