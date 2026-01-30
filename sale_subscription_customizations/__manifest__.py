{
    'name': 'Sale Subscription Customizations',
    'version': '18.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Customizzazioni modulo Abbonamenti',
    'description': """
        Customizzazioni per il modulo Sale Subscription:
        - Campo durata abbonamento (mesi/anni) con calcolo automatico data fine
        - Data inizio NON valorizzata automaticamente alla conferma preventivo
        - Data inizio copiata dalla "Data consegna impegnata" (modificabile)
        - Calcolo automatico data fine = data inizio + durata
        - Alert attività assegnata al venditore 1 mese prima della scadenza
        - Campo "Codice Noleggio" per identificare univocamente gli abbonamenti
        - Codice Noleggio visibile nelle righe fattura e nel report PDF
    """,
    'author': 'Mistral',
    'website': '',
    'depends': ['sale_subscription', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'report/report_invoice.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
