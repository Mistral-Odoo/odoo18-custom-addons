{
    'name': 'Project Customizations',
    'version': '18.0.2.0.0',
    'category': 'Services/Project',
    'summary': 'Personalizzazioni modulo Progetti',
    'description': 'Personalizzazioni progetto: mail assegnazione con cliente, '
                   'rapportino on-site, export timesheet per cliente in ZIP Excel.',
    'author': 'Mistral Digital Solutions s.r.l',
    'website': 'https://www.mistralsolutions.it',
    'depends': ['project', 'hr_timesheet', 'helpdesk_timesheet', 'sale_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_templates.xml',
        'views/project_project_stage_views.xml',
        'views/project_task_type_views.xml',
        'views/account_analytic_line_views.xml',
        'views/timesheet_export_wizard_views.xml',
        'report/report_rapportino_onsite.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
