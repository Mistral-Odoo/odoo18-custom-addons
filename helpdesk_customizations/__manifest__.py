{
    'name': 'Helpdesk Customizations',
    'version': '18.0.1.1.0',
    'category': 'Services/Helpdesk',
    'summary': 'Customizzazioni modulo Helpdesk',
    'description': """
        Customizzazioni per il modulo Helpdesk:
        - Ticket chiuso non modificabile ma riapribile (con permessi speciali)
        - Blocco spostamento a fasi precedenti dopo risoluzione
        - Numero ticket sempre visibile nel breadcrumb (display_name)
        - Preservazione data chiusura nelle fasi post-risoluzione
        - Campo "Ticket Sola Lettura" sugli stage
        - Blocco tab Fogli Ore su ticket in fase readonly
    """,
    'author': 'Mistral',
    'website': '',
    'depends': ['helpdesk', 'helpdesk_timesheet'],
    'data': [
        'security/helpdesk_security.xml',
        'views/helpdesk_stage_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_timesheet_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
