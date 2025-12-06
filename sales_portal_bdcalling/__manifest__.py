
{
    'name': "sales portal bdcalling",
    'version': '1.0',
    'summary': "Manage sales portal bdcalling, fans, and temperature controls",
    'description': """
        This module allows users to manage ventilation farms.
        Features include:
        - Store farm details
        - Manage ventilation fans
        - Set target temperatures
        - Prevent duplicate fan entries
        - Track temperature changes over time
    """,


    'author': "Afzal Khan",
    'website': "https://www.example.com",
    'category': 'Bdcalling Portal',
    'depends': ['base', 'mail','sale' ,'hr'],  
    'data': [
        'views/sale_order_inherit_view.xml',
        'views/team_views.xml',
        'views/platform_source_views.xml',
        'views/profile_name_views.xml',
        'views/order_source_views.xml',
        'views/empolyee_assign_team_views.xml',
        'security/ir.model.access.csv',
        'views/product_inheritance_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
