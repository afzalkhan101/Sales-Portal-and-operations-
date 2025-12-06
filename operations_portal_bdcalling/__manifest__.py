
{
    'name': "Operations portal bedcalling",
    'version': '1.0',
    'summary': "Manage sales portal bdcalling, fans, and temperature controls",
    'description': "",
    'author': "Afzal Khan",
    'website': "https://www.example.com",
    'category': 'Bdcalling Portal',
    'depends': ['base', 'mail','sale' ,'hr' ,'sales_portal_bdcalling'],  
    'data': [
        'security/ir.model.access.csv',
        'views/operations_views.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
