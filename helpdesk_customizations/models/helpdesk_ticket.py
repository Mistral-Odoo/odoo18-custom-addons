from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Campo per la soluzione del ticket (separato dalla descrizione/richiesta)
    solution = fields.Html(
        string='Soluzione',
        help='Descrizione della soluzione adottata per risolvere il ticket'
    )

    # Campo per il nome del richiedente (inserito manualmente)
    requester_name = fields.Char(
        string='Nome Richiedente',
        help='Nome della persona che ha effettuato la richiesta'
    )

    # Campo per sbloccare temporaneamente il ticket per modifiche
    is_reopened = fields.Boolean(
        string='Is Reopened',
        default=False,
        help='True se il ticket è stato riaperto per modifiche'
    )

    # Campo computed per identificare se il ticket è in uno stage "chiuso"
    # Basato sul campo is_readonly_stage dello stage
    is_closed_stage = fields.Boolean(
        string='Is Closed Stage',
        compute='_compute_is_closed_stage',
        store=True,
        help='True se il ticket è in uno stage con is_readonly_stage=True'
    )

    @api.depends('stage_id', 'stage_id.is_readonly_stage', 'is_reopened')
    def _compute_is_closed_stage(self):
        for ticket in self:
            if ticket.is_reopened:
                # Se il ticket è stato riaperto, non è readonly
                ticket.is_closed_stage = False
            elif ticket.stage_id:
                # Usa il campo is_readonly_stage dello stage
                ticket.is_closed_stage = ticket.stage_id.is_readonly_stage
            else:
                ticket.is_closed_stage = False

    # Override display_name per mostrare il numero ticket PRIMA del titolo
    # Adattato per Odoo 18 che usa una struttura diversa
    @api.depends('ticket_ref', 'name', 'partner_name')
    @api.depends_context('with_partner')
    def _compute_display_name(self):
        display_partner_name = self._context.get('with_partner', False)
        for ticket in self:
            if ticket.ticket_ref:
                # Formato: "#TIC-25-20385 - Titolo del ticket"
                name = f"#{ticket.ticket_ref}"
                if ticket.name:
                    name += f" - {ticket.name}"
            else:
                name = ticket.name or ''

            if display_partner_name and ticket.partner_name:
                name += f" - {ticket.partner_name}"

            ticket.display_name = name

    def _user_can_reopen_ticket(self):
        """
        Verifica se l'utente corrente ha i permessi per riaprire/spostare ticket chiusi.
        """
        return self.env.user.has_group(
            'helpdesk_customizations.group_helpdesk_reopen_ticket'
        )

    def _check_stage_change_allowed(self, new_stage_id):
        """
        Verifica se lo spostamento a una nuova fase è consentito.
        Blocca lo spostamento a fasi precedenti per ticket in fase readonly,
        a meno che l'utente non abbia permessi speciali.
        """
        if not new_stage_id:
            return

        new_stage = self.env['helpdesk.stage'].browse(new_stage_id)

        for ticket in self:
            # Se il ticket non è in una fase readonly, permetti qualsiasi spostamento
            if not ticket.stage_id.is_readonly_stage:
                continue

            # Se l'utente ha permessi speciali, permetti lo spostamento
            if ticket._user_can_reopen_ticket():
                continue

            # Se il ticket è stato riaperto, permetti lo spostamento
            if ticket.is_reopened:
                continue

            # Blocca lo spostamento a fasi con sequence inferiore
            if new_stage.sequence < ticket.stage_id.sequence:
                raise UserError(_(
                    "Non è possibile spostare il ticket '%(ticket)s' alla fase '%(stage)s' "
                    "perché è già stato risolto. Contatta un amministratore se necessario.",
                    ticket=ticket.display_name,
                    stage=new_stage.name,
                ))

    def write(self, vals):
        # Verifica se lo spostamento di fase è consentito
        if vals.get('stage_id'):
            self._check_stage_change_allowed(vals['stage_id'])

        # Reset is_reopened quando si cambia stage
        if vals.get('stage_id') and 'is_reopened' not in vals:
            vals['is_reopened'] = False

        # Gestione preservazione close_date
        # Salviamo le close_date esistenti prima della write
        preserved_close_dates = {}
        if vals.get('stage_id'):
            for ticket in self:
                if ticket.close_date:
                    preserved_close_dates[ticket.id] = ticket.close_date

        # Chiamata al metodo originale
        res = super().write(vals)

        # Ripristino close_date per i ticket che l'avevano già
        # Questo mantiene la data di chiusura originale quando si sposta
        # un ticket già chiuso in un'altra fase post-risoluzione
        if preserved_close_dates:
            for ticket in self:
                if ticket.id in preserved_close_dates and not ticket.close_date:
                    # Ripristina la close_date senza triggerare altri eventi
                    super(HelpdeskTicket, ticket).write({
                        'close_date': preserved_close_dates[ticket.id]
                    })

        return res

    def action_reopen_ticket(self):
        """
        Riapre un ticket per permettere modifiche senza cambiare lo stage.
        Richiede permessi speciali.
        """
        for ticket in self:
            if not ticket._user_can_reopen_ticket():
                raise UserError(_(
                    "Non hai i permessi per riaprire questo ticket. "
                    "Contatta un amministratore."
                ))
            ticket.is_reopened = True
