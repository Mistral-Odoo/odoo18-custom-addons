from odoo import fields, models


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    is_to_invoice = fields.Boolean(
        string='Da Fatturare',
        default=False,
        help='Se abilitato, i progetti in questa fase saranno inclusi nell\'export timesheet.',
    )
