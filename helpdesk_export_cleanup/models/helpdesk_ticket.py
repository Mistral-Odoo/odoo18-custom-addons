import re

from odoo import models
from odoo.tools.mail import html_to_inner_content


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        res = super()._export_rows(fields, _is_toplevel_call=_is_toplevel_call)
        if not _is_toplevel_call:
            return res

        desc_indices = [
            i for i, field_path in enumerate(fields)
            if field_path and field_path[0] == 'description'
        ]

        if desc_indices:
            for row in res:
                for idx in desc_indices:
                    if idx < len(row) and row[idx]:
                        text = html_to_inner_content(str(row[idx]))
                        # Rimuovi eventuali stringhe base64 residue
                        text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]{50,}', '', text)
                        # Rimuovi sequenze di 50+ cifre consecutive (ID numerici di immagini)
                        text = re.sub(r'\d{50,}', '', text)
                        # Pulisci spazi multipli risultanti
                        text = re.sub(r' {2,}', ' ', text).strip()
                        row[idx] = text
        return res
