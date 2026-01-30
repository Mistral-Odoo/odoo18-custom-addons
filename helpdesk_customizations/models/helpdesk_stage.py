from odoo import fields, models


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_readonly_stage = fields.Boolean(
        string='Ticket Sola Lettura',
        default=False,
        help='Se abilitato, i ticket in questa fase saranno in sola lettura '
             '(non modificabili). Usare per fasi come Risolto, Da fatturare, etc.'
    )
