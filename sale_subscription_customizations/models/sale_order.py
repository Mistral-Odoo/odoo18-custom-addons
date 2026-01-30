from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Campi per la durata dell'abbonamento
    subscription_duration = fields.Integer(
        string='Durata Abbonamento',
        default=0,
        help='Durata dell\'abbonamento. Se 0 o vuoto, l\'abbonamento non ha scadenza.'
    )

    subscription_duration_unit = fields.Selection(
        selection=[
            ('months', 'Mesi'),
            ('years', 'Anni'),
        ],
        string='Unità Durata',
        default='months',
        help='Unità di misura per la durata dell\'abbonamento.'
    )

    # Campo computed per mostrare se l'abbonamento ha una scadenza
    has_subscription_end = fields.Boolean(
        string='Ha Scadenza',
        compute='_compute_has_subscription_end',
        store=True,
        help='True se l\'abbonamento ha una data di scadenza definita.'
    )

    # Campo per tracciare se l'alert di scadenza è stato già creato
    expiration_alert_sent = fields.Boolean(
        string='Alert Scadenza Inviato',
        default=False,
        help='True se l\'attività di alert per la scadenza è già stata creata.'
    )

    # Campo per identificare univocamente il noleggio/abbonamento nelle fatture
    codice_noleggio = fields.Char(
        string='Codice Noleggio',
        help='Codice identificativo univoco del noleggio/abbonamento. '
             'Verrà riportato nelle righe fattura per identificare la provenienza.'
    )

    @api.depends('subscription_duration')
    def _compute_has_subscription_end(self):
        for order in self:
            order.has_subscription_end = order.subscription_duration > 0

    def _compute_start_date(self):
        """
        Override del compute standard.
        NON valorizza automaticamente start_date con la data odierna.
        start_date verrà valorizzato solo quando l'utente compila commitment_date.
        """
        for so in self:
            if not so.is_subscription:
                so.start_date = False
            # NON impostiamo start_date = today() come fa il modulo standard
            # Lo start_date verrà impostato solo quando commitment_date viene valorizzato

    def _compute_next_invoice_date(self):
        """
        Override del compute standard.
        NON valorizza next_invoice_date con today() se start_date è vuoto.
        next_invoice_date verrà valorizzato solo quando start_date è presente.
        """
        for so in self:
            if not so.is_subscription and so.subscription_state != '7_upsell':
                so.next_invoice_date = False
            elif not so.next_invoice_date and so.state == 'sale':
                # Modifica: impostiamo next_invoice_date SOLO se start_date è valorizzato
                if so.start_date:
                    so.next_invoice_date = so.start_date
                # Se start_date è vuoto, lasciamo vuoto anche next_invoice_date

    def _set_deferred_end_date_from_template(self):
        """
        Override per non impostare end_date se start_date è vuoto.
        """
        # Chiamiamo il metodo originale solo se start_date è valorizzato
        if self.start_date:
            super()._set_deferred_end_date_from_template()
        # Se start_date è vuoto, non facciamo nulla

    @api.onchange('commitment_date')
    def _onchange_commitment_date_to_start_date(self):
        """
        Quando viene valorizzata la data consegna impegnata,
        copia il valore nel campo start_date (solo la data, senza ora).
        Popola start_date solo se è vuoto, così l'utente può modificarlo successivamente
        senza che venga sovrascritto.
        """
        if self.commitment_date and self.is_subscription:
            # commitment_date è Datetime, start_date è Date
            # Popola start_date solo se è vuoto (prima valorizzazione)
            if not self.start_date:
                self.start_date = self.commitment_date.date()
            # Aggiorniamo anche next_invoice_date se vuoto
            if not self.next_invoice_date:
                self.next_invoice_date = self.commitment_date.date()

    def write(self, vals):
        """
        Override write per:
        1. Bloccare la scrittura automatica di start_date se commitment_date è vuoto
           MA permettere la modifica manuale se commitment_date è già valorizzato
        2. Copiare commitment_date in start_date quando viene valorizzato per la prima volta
        3. Ricalcolare end_date quando necessario
        """
        for order in self:
            # Se è una subscription e commitment_date è vuoto,
            # blocca la scrittura automatica di start_date, next_invoice_date, end_date
            if order.is_subscription and not order.commitment_date:
                # Rimuovi le date dai vals se non c'è commitment_date
                # a meno che non stia venendo scritto commitment_date stesso
                if 'commitment_date' not in vals or not vals.get('commitment_date'):
                    if 'start_date' in vals and vals['start_date']:
                        # Blocca: non permettere di impostare start_date automaticamente
                        vals.pop('start_date', None)
                    if 'next_invoice_date' in vals and vals['next_invoice_date'] and not order.start_date:
                        vals.pop('next_invoice_date', None)
                    if 'end_date' in vals and vals['end_date'] and not order.start_date:
                        vals.pop('end_date', None)
            # Se commitment_date è già valorizzato, permettiamo la modifica di start_date
            # (l'utente può modificare manualmente la data di inizio)

        # Se viene scritto commitment_date per la prima volta, aggiorniamo anche start_date
        # MA solo se start_date non è già stato modificato manualmente
        if 'commitment_date' in vals and vals['commitment_date']:
            # Verifichiamo se è un nuovo commitment_date (non una modifica)
            for order in self:
                if not order.commitment_date:
                    # commitment_date viene valorizzato per la prima volta
                    commitment_dt = vals['commitment_date']
                    if isinstance(commitment_dt, str):
                        from odoo import fields as odoo_fields
                        commitment_dt = odoo_fields.Datetime.from_string(commitment_dt)
                    if hasattr(commitment_dt, 'date'):
                        new_date = commitment_dt.date()
                    else:
                        new_date = commitment_dt
                    # Imposta start_date solo se non è già nei vals (modifica manuale)
                    if 'start_date' not in vals:
                        vals['start_date'] = new_date
                    if 'next_invoice_date' not in vals:
                        vals['next_invoice_date'] = new_date
                    break  # Evitiamo di processare più volte

        res = super().write(vals)

        # Se sono stati modificati i campi rilevanti, ricalcola end_date
        if any(f in vals for f in ['start_date', 'subscription_duration', 'subscription_duration_unit']):
            for order in self:
                if order.is_subscription and order.start_date:
                    order._compute_end_date_from_duration()
                    # Se start_date è cambiato, aggiorna anche next_invoice_date
                    # solo se next_invoice_date era uguale al vecchio start_date o vuoto
                    if 'start_date' in vals:
                        if not order.next_invoice_date or order.next_invoice_date < order.start_date:
                            order.next_invoice_date = order.start_date

        return res

    def action_confirm(self):
        """
        Override di action_confirm per evitare che start_date e next_invoice_date
        vengano impostati automaticamente a oggi alla conferma.
        """
        # Salviamo se commitment_date è vuoto PRIMA della conferma
        orders_without_commitment = {
            order.id: not order.commitment_date
            for order in self
            if order.is_subscription
        }

        # Chiamiamo il metodo originale
        res = super().action_confirm()

        # Per gli ordini senza commitment_date, resettiamo le date
        for order in self:
            if order.id in orders_without_commitment and orders_without_commitment[order.id]:
                # Forza il reset usando SQL diretto
                self.env.cr.execute("""
                    UPDATE sale_order
                    SET start_date = NULL,
                        next_invoice_date = NULL,
                        end_date = NULL
                    WHERE id = %s
                """, (order.id,))

        # Invalida la cache per questi record
        self.invalidate_recordset(['start_date', 'next_invoice_date', 'end_date'])

        return res

    @api.depends('start_date', 'subscription_duration', 'subscription_duration_unit')
    def _compute_end_date_from_duration(self):
        """
        Calcola la data di fine abbonamento basandosi su:
        - start_date + subscription_duration (in mesi o anni)
        Se subscription_duration è 0 o vuoto, end_date non viene impostata.
        """
        for order in self:
            if order.start_date and order.subscription_duration > 0:
                if order.subscription_duration_unit == 'months':
                    order.end_date = order.start_date + relativedelta(
                        months=order.subscription_duration
                    )
                elif order.subscription_duration_unit == 'years':
                    order.end_date = order.start_date + relativedelta(
                        years=order.subscription_duration
                    )
            # Se duration è 0, non modifichiamo end_date (abbonamento senza scadenza)

    @api.onchange('start_date', 'subscription_duration', 'subscription_duration_unit')
    def _onchange_compute_end_date(self):
        """
        Onchange per ricalcolare end_date quando cambiano i parametri.
        Aggiorna anche next_invoice_date se necessario.
        """
        self._compute_end_date_from_duration()
        # Se start_date è valorizzato, aggiorna next_invoice_date
        # se è vuoto o se era precedente alla nuova start_date
        if self.start_date:
            if not self.next_invoice_date or self.next_invoice_date < self.start_date:
                self.next_invoice_date = self.start_date

    @api.model
    def _cron_create_expiration_alerts(self):
        """
        Cron job che crea attività per gli ordini in abbonamento
        che scadono entro 1 mese.
        """
        today = fields.Date.today()
        one_month_later = today + relativedelta(months=1)

        # Cerca abbonamenti attivi con scadenza entro 1 mese
        # che non hanno già ricevuto l'alert
        orders_to_alert = self.search([
            ('is_subscription', '=', True),
            ('subscription_state', '=', '3_progress'),  # In corso
            ('end_date', '!=', False),
            ('end_date', '<=', one_month_later),
            ('end_date', '>', today),  # Non già scaduti
            ('expiration_alert_sent', '=', False),
        ])

        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([
                ('name', 'ilike', 'To Do')
            ], limit=1)

        for order in orders_to_alert:
            # Crea attività assegnata al venditore dell'ordine
            user_id = order.user_id.id if order.user_id else self.env.user.id

            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get_id('sale.order'),
                'res_id': order.id,
                'activity_type_id': activity_type.id if activity_type else False,
                'summary': _('Abbonamento in scadenza'),
                'note': _(
                    'L\'abbonamento %s scade il %s. '
                    'Contattare il cliente per il rinnovo.',
                    order.name,
                    order.end_date.strftime('%d/%m/%Y') if order.end_date else ''
                ),
                'date_deadline': today,
                'user_id': user_id,
            })

            # Segna l'alert come inviato
            order.expiration_alert_sent = True
