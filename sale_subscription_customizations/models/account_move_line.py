from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    codice_noleggio = fields.Char(
        string='Codice Noleggio',
        help='Codice noleggio proveniente dall\'ordine di vendita in abbonamento.',
        copy=False
    )
