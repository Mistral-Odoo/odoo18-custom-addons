from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_code = fields.Char(
        string='Codice Prodotto',
        copy=False,
    )
    serial_number = fields.Char(
        string='Serial Number',
        copy=False,
    )
