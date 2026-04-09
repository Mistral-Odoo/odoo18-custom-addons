{
    'name': 'Sale Order Line Customizations',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Aggiunge serial number e codice prodotto sulle righe ordine e fattura',
    'description': 'Aggiunge i campi serial number e codice prodotto sulle righe '
                   'dell\'ordine di vendita, con propagazione nelle righe fattura e PDF.',
    'author': 'Mistral Digital Solutions s.r.l',
    'website': 'https://www.mistralsolutions.it',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'report/report_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
