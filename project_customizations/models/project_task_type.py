from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_to_invoice = fields.Boolean(
        string='Da Fatturare',
        default=False,
        help='Se abilitato, i lavori in questa fase saranno inclusi nell\'export timesheet.',
    )
