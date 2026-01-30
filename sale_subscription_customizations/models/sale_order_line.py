from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        """
        Override per propagare il codice noleggio dall'ordine di vendita
        alla riga fattura.
        """
        res = super()._prepare_invoice_line(**optional_values)

        # Propaga il codice noleggio dall'ordine di vendita
        # solo se l'ordine ha un piano ricorrente e un codice noleggio
        if self.order_id.plan_id and self.order_id.codice_noleggio:
            res['codice_noleggio'] = self.order_id.codice_noleggio

        return res
