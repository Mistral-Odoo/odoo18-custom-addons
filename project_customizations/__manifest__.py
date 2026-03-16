{
    'name': 'Project Customizations',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Personalizzazioni modulo Progetti',
    'description': 'Aggiunge il nome del cliente nelle mail di assegnazione lavoro.',
    'author': 'Mistral Digital Solutions s.r.l',
    'website': 'https://www.mistralsolutions.it',
    'depends': ['project', 'hr_timesheet', 'helpdesk_timesheet'],
    'data': [
        'views/mail_templates.xml',
        'report/report_rapportino_onsite.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
