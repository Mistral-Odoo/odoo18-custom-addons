from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_code = fields.Char(
        string='Codice Prodotto',
        help='Codice prodotto specifico per questo preventivo/ordine.',
    )
    serial_number = fields.Char(
        string='Serial Number',
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.product_code:
            res['product_code'] = self.product_code
        if self.serial_number:
            res['serial_number'] = self.serial_number
        return res
