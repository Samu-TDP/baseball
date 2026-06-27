import flet as ft
from database.DAO import DAO

class Controller:
    def __init__(self, view, model):
        """
        COSTRUTTORE DEL CONTROLLER: Connette i tre pilastri dell'architettura MVC.
        - self._view: Riferimento all'interfaccia utente grafica.
        - self._model: Riferimento al motore logico (grafo stazionario e ricorsione).
        """
        self._view = view
        self._model = model

    # =========================================================================
    # PATTERN MECCANICO 1: INIZIALIZZAZIONE AL BOOT (popola_anni)
    # RISPONDE A: PUNTO 1.a -> Caricare gli anni disponibili a partire dal 1980.
    # =========================================================================
    def popola_anni(self):
        """
        Viene invocato nel main.py subito dopo l'avvio dell'interfaccia grafica.
        Riempie la prima tendina degli anni recuperando i dati pre-caricati nel Model.
        """
        try:
            # 1. Recuperiamo la lista degli anni memorizzati nel Model all'avvio
            anni_disponibili = self._model.get_all_years()

            # 2. Svuotamento preventivo di sicurezza del Dropdown della View
            self._view._ddAnno.options.clear()

            # 3. Popolamento delle opzioni grafiche di Flet
            for anno in anni_disponibili:
                self._view._ddAnno.options.append(
                    ft.dropdown.Option(key=str(anno), text=f"Stagione {anno}")
                )

            # --- SBLOCCO STRATEGICO REATTIVO (PUNTO 1.b) ---
            # Assegniamo la funzione handle_seleziona_anno all'attributo on_change della tendina.
            self._view._ddAnno.on_change = self.handle_seleziona_anno

            # 4. Rinfreschiamo lo schermo grafico
            self._view.update_page()

        except Exception as ex:
            print(f"[ERRORE BOOT POPOLAMENTO ANNI]: {ex}")

    # =========================================================================
    # PATTERN MECCANICO 2: INTERCETTAZIONE SELEZIONE ANNO (handle_seleziona_anno)
    # RISPONDE A: PUNTO 1.b -> Stampa istantanea delle squadre iscritte nell'anno
    # e caricamento contestuale della seconda tendina 'Squadra'.
    # =========================================================================
    def handle_seleziona_anno(self, e):
        """
        Metodo attivato automaticamente non appena l'utente sceglie un anno dal dropdown.
        Sfrutta la id_map dei nodi stabili per evitare duplicazioni di istanze in RAM.
        """
        # 1. Recuperiamo il valore dell'anno scelto come stringa
        anno_str = self._view._ddAnno.value
        if anno_str is None:
            return

        anno_int = int(anno_str)

        # 2. Puliamo i contenitori grafici deputati a mostrare le squadre
        self._view._txtOutSquadre.controls.clear()

        # 3. Chiamiamo il DAO con il nuovo metodo getAllNodes passando la id_map del Model
        squadre_trovate = DAO.getAllNodes(anno_int, self._model._id_map_teams)

        # 4. Stampiamo il numero totale e inseriamo l'elenco delle sigle (teamCode)
        self._view._txtOutSquadre.controls.append(
            ft.Text(f"Trovate {len(squadre_trovate)} squadre nel {anno_int}:", weight="bold", color="blue")
        )

        # 5. Puliamo e prepariamo la seconda tendina delle Squadre (self._view._ddSquadra)
        self._view._ddSquadra.options.clear()

        # 6. Ciclo unificato per riempire la ListView delle sigle ed il Dropdown
        for team in squadre_trovate:
            # Appendiamo la sigla (teamCode) e il nome nella ListView delle squadre
            self._view._txtOutSquadre.controls.append(
                ft.Text(f"  • {team.teamCode} - {team.name}")
            )
            # Aggiungiamo l'oggetto nel secondo dropdown per i punti successivi
            # key = teamCode (stringa), text = Sigla e nome completo
            self._view._ddSquadra.options.append(
                ft.dropdown.Option(key=team.teamCode, text=f"{team.teamCode} - {team.name}")
            )

        # 7. Forziamo l'aggiornamento della View
        self._view.update_page()

    # =========================================================================
    # PATTERN MECCANICO 3: CREAZIONE DEL GRAFO (handleCreaGrafo)
    # RISPONDE A: PUNTO 1.c & 1.d -> Click sul pulsante 'Crea Grafo'
    # =========================================================================
    def handleCreaGrafo(self, e):
        """
        Metodo attivato dal click su self._view._btnCreaGrafo.
        Ordina al Model di erigere il grafo completo tramite il metodo corretto 'crea_grafo'.
        """
        # 1. Pulizia totale della bacheca dei risultati principali (self._view._txt_result)
        self._view._txt_result.controls.clear()

        # 2. Scudo di controllo dell'input
        anno_str = self._view._ddAnno.value
        if anno_str is None:
            self._view._txt_result.controls.append(
                ft.Text("Errore: Selezionare prima un anno dal menu a tendina.", color="red", weight="bold")
            )
            self._view.update_page()
            return

        anno_int = int(anno_str)

        # 3. ADEGUAMENTO: Chiamata a 'crea_grafo' (restituisce n_nodi, n_archi) come definito nel nuovo Model
        nodi_totali, archi_totali = self._model.crea_grafo(anno_int)

        # 4. Stampa di successo a video
        self._view._txt_result.controls.append(
            ft.Text("Grafo completo correttamente generato in memoria!", color="green", weight="bold")
        )
        self._view._txt_result.controls.append(ft.Text(f"Numero totale di vertici (Squadre): {nodi_totali}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero totale di archi (Collegamenti): {archi_totali}"))

        # 5. Rinfresco dello schermo
        self._view.update_page()

    # =========================================================================
    # PATTERN MECCANICO 4: INTERROGAZIONE VICINI ORDINATI (handleDettagli)
    # RISPONDE A: PUNTO 1.e -> Click sul pulsante 'Dettagli'
    # =========================================================================
    def handleDettagli(self, e):
        """
        Metodo attivato dal click su self._view._btnDettagli.
        Isola la squadra scelta, estrae i nodi adiacenti tramite getViciniOrdinati.
        """
        # 1. Puliamo l'area dei risultati mantenendo i log del grafo
        self._view._txt_result.controls.clear()

        # 2. ADEGUAMENTO: Controllo della presenza del grafo tramite l'attributo corretto '_grafo'
        if self._model._grafo.number_of_nodes() == 0:
            self._view._txt_result.controls.append(
                ft.Text("Errore: Generare prima il grafo cliccando su 'Crea Grafo'.", color="red", weight="bold")
            )
            self._view.update_page()
            return

        # 3. Scudo di sicurezza: l'utente ha selezionato una squadra dal secondo menu?
        team_selezionato_code = self._view._ddSquadra.value
        if team_selezionato_code is None:
            self._view._txt_result.controls.append(
                ft.Text("Errore: Selezionare una squadra dal menu a tendina 'Squadra' per vederne i dettagli.",
                        color="red", weight="bold")
            )
            self._view.update_page()
            return

        # 4. ADEGUAMENTO: Traduzione identità tramite la mappa corretta '_id_map_teams'
        team_sorgente = self._model._id_map_teams[team_selezionato_code]

        # 5. Delega logica al Model per ottenere i vicini ordinati con getViciniOrdinati
        vicini_pesati = self._model.getViciniOrdinati(team_sorgente)

        # 6. Impaginazione a schermo dei risultati ordinati
        self._view._txt_result.controls.append(
            ft.Text(f"Elenco delle squadre adiacenti a {team_sorgente.name} in ordine decrescente di spesa:",
                    color="purple", weight="bold")
        )

        for vicino, peso in vicini_pesati:
            # Trasformiamo la cifra in milioni di dollari per arricchire l'output
            milioni_dollari = round(peso / 1_000_000, 2)
            self._view._txt_result.controls.append(
                ft.Text(f"  └──► {vicino.teamCode} - {vicino.name} | Somma Salari: ${peso:,.2f} ({milioni_dollari}M $)")
            )

        # 7. Aggiornamento grafico della pagina
        self._view.update_page()

    # =========================================================================
    # PATTERN MECCANICO 5: RICORSIONE / BACKTRACKING (handlePercorso)
    # RISPONDE A: PUNTO 2 -> Click sul pulsante 'Percorso'
    # =========================================================================
    def handlePercorso(self, e):
        """
        Metodo attivato dal click su self._view._btnPercorso.
        Lancia l'algoritmo di ottimizzazione esaustiva ad archi decrescenti.
        """
        # 1. Pulizia totale dello schermo per evidenziare il percorso ottimo
        self._view._txt_result.controls.clear()

        # 2. ADEGUAMENTO: Scudi preventivi di stabilità sulla presenza reale del grafo controllando '_grafo'
        if self._model._grafo.number_of_nodes() == 0:
            self._view._txt_result.controls.append(
                ft.Text("Errore: È obbligatorio creare il grafo prima di cercare il percorso massimo.", color="red",
                        weight="bold")
            )
            self._view.update_page()
            return

        team_selezionato_code = self._view._ddSquadra.value
        if team_selezionato_code is None:
            self._view._txt_result.controls.append(
                ft.Text(
                    "Errore: Selezionare una squadra dal menu 'Squadra' come vertice di partenza per la ricorsione.",
                    color="red", weight="bold")
            )
            self._view.update_page()
            return

        # 3. ADEGUAMENTO: Traduzione del codice stringa in Oggetto Team reale usando la mappa corretta '_id_map_teams'
        team_partenza = self._model._id_map_teams[team_selezionato_code]

        # 4. Messaggio temporaneo UX di caricamento
        self._view._txt_result.controls.append(
            ft.Text("Ricerca esaustiva del cammino a peso massimo ed archi decrescenti in corso... Attendere.",
                    color="orange", italic=True)
        )
        self._view.update_page()

        # 5. DELEGA LOGICA AL MOTORE RICORSIVO DEL MODEL
        percorso_ottimo, peso_totale_ottimo = self._model.cerca_percorso_massimo(team_partenza)

        # Rimuoviamo la scritta temporanea "In corso..."
        self._view._txt_result.controls.clear()

        # 6. IMPAGINAZIONE CONCLUSIVA DEI RISULTATI DELLA RICORSIONE
        if not percorso_ottimo or len(percorso_ottimo) <= 1:
            self._view._txt_result.controls.append(
                ft.Text("Nessun cammino ad archi decrescenti trovato a partire dalla squadra selezionata.", color="red",
                        weight="bold")
            )
        else:
            self._view._txt_result.controls.append(
                ft.Text("Percorso ottimo ricorsivo individuato con successo!", color="green", weight="bold", size=16)
            )
            self._view._txt_result.controls.append(
                ft.Text(f"PESO TOTALE DEL PERCORSO OTTOMIZZATO: ${peso_totale_ottimo:,.2f}", color="blue",
                        weight="bold")
            )
            self._view._txt_result.controls.append(
                ft.Text(f"Sviluppo sequenziale delle {len(percorso_ottimo)} tappe del cammino:"))

            # Stampiamo il primo nodo capofila della spedizione
            self._view._txt_result.controls.append(
                ft.Text(f"Partenza ──► {percorso_ottimo[0].teamCode} ({percorso_ottimo[0].name})"))

            # ADEGUAMENTO: Ciclo per estrarre i pesi esatti arco per arco dal grafo corretto '_grafo'
            for i in range(1, len(percorso_ottimo)):
                antecedente = percorso_ottimo[i - 1]
                corrente = percorso_ottimo[i]

                # Accediamo alla RAM di NetworkX tramite '_grafo'
                peso_tratta = self._model._grafo[antecedente][corrente]['weight']

                self._view._txt_result.controls.append(
                    ft.Text(
                        f"   └───► Tratta {i} (Valore arco: ${peso_tratta:,.2f}) ──► {corrente.teamCode} ({corrente.name})")
                )

        # 7. Aggiornamento conclusivo dei controlli della pagina
        self._view.update_page()