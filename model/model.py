import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        """Inizializza l'applicazione configurando la mappa d'identità dei nodi stabili."""
        self._all_years = DAO.getAllYears()
        self._all_teams = DAO.getAllTeams()

        # Identity Map cruciale: associa ogni codice stringa ad un unico oggetto Team in RAM
        self._id_map_teams = {}
        for team in self._all_teams:
            self._id_map_teams[team.teamCode] = team

        self._grafo = nx.Graph()  # Grafo semplice non orientato richiesto

    def crea_grafo(self, anno):
        """Costruisce il grafo accoppiando i nodi unici senza frammentazione di istanze."""
        self._grafo.clear()

        # STEP 1: Recupero dei nodi unici tramite la query setaccio DISTINCT
        nodes = DAO.getAllNodes(anno, self._id_map_teams)
        self._grafo.add_nodes_from(nodes)

        # STEP 2: Recupero del dizionario dei budget salariali dell'anno
        salari = DAO.getSalariSquadre(anno)

        # STEP 3: Doppio ciclo combinatorio sfasato ad indici (i, j)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                squadra1 = nodes[i]
                squadra2 = nodes[j]

                # Inizializzazione di scudo a 0 se il team non ha salari registrati nell'anno
                salario1 = 0
                salario2 = 0

                if squadra1.teamCode in salari:
                    salario1 = salari[squadra1.teamCode]

                if squadra2.teamCode in salari:
                    salario2 = salari[squadra2.teamCode]

                # Il peso dell'arco è la somma dei salari delle due compagini
                peso = salario1 + salario2

                # Aggiungiamo l'arco non orientato pesato
                self._grafo.add_edge(squadra1, squadra2, weight=peso)

        return self._grafo.number_of_nodes(), self._grafo.number_of_edges()

    def get_all_years(self):
        return list(self._all_years)

    def get_all_squadre(self):
        return list(self._grafo.nodes)

    def getViciniOrdinati(self, squadra):
        """Isola i vicini adiacenti ordinandoli per budget decrescente."""
        if not self._grafo.has_node(squadra):
            return []

        viciniT = []
        # Esploriamo i nodi adiacenti recuperando il peso dell'arco associato
        for v in self._grafo.neighbors(squadra):
            peso = self._grafo[squadra][v]["weight"]
            viciniT.append((v, peso))

        # Ordinamento decrescente basato sul peso (indice 1 della tupla)
        viciniT.sort(key=lambda x: x[1], reverse=True)
        return viciniT

    # =========================================================================
    # FUNZIONE 3: ALGORITMO DI BACKTRACKING RICORSIVO (PUNTO 2)
    # =========================================================================
    def cerca_percorso_massimo(self, nodo_partenza):
        """
        COSA FA: Configura la bacheca dei record ed accende il motore ricorsivo.
        STRUTTURA DATI DI RITORNO: (lista_oggetti_Team_ottima, peso_massimo_cumulato).
        """
        # 1. Reset dei record globali prima dell'avvio
        self._best_path_ricorsione = []
        self._best_weight_ricorsione = 0.0

        # 2. Inizializzazione della valigia parziale con il nodo capofila scelto nella UI
        parziale = [nodo_partenza]

        # 3. Lancio del motore esaustivo (Impostiamo l'ultimo peso a infinito per promuovere qualsiasi primo passo)
        self._backtracking_esaustivo(parziale, ultimo_peso_limite=float('inf'), peso_accumulato=0.0)

        return self._best_path_ricorsione, self._best_weight_ricorsione

    def _backtracking_esaustivo(self, parziale, ultimo_peso_limite, peso_accumulato):
        """Motore ricorsivo in profondità (DFS) ad ottimizzazione vincolata."""

        # CASO BASE DINAMICO: Controlliamo ad ogni passo se abbiamo migliorato il medagliere del peso massimo
        if peso_accumulato > self._best_weight_ricorsione:
            self._best_weight_ricorsione = peso_accumulato
            # Eseguiamo una copia fisica della lista per tutelare l'istantanea in memoria
            self._best_path_ricorsione = list(parziale)
            # NOTA BENE: Non inseriamo 'return', altrimenti impediamo l'aggancio di altre tappe valide in coda!

        # Identifichiamo il vertice terminale attuale della catena di viaggio
        nodo_attuale = parziale[-1]

        # Esploriamo i vicini adiacenti del nodo corrente
        for vicino in self._grafo.neighbors(nodo_attuale):

            # VINCOLO A: 'Ogni vertice può comparire una sola volta' (Scudo anti-ciclo)
            if vicino not in parziale:

                # Estraiamo il peso memorizzato nell'arco di NetworkX
                peso_tratta = self._grafo[nodo_attuale][vicino]['weight']

                # VINCOLO B: 'Il peso degli archi nel percorso deve essere strettamente decrescente'
                if peso_tratta < ultimo_peso_limite:
                    # --- LA SACRA TRINITÀ DEL BACKTRACKING ---
                    parziale.append(vicino)  # 1. DO: Effettuo il passo in avanti inserendo il team

                    # 2. RECURSION: Avanzo nel ramo passando il peso corrente come limite ed incrementando il cumulatore
                    self._backtracking_esaustivo(
                        parziale,
                        ultimo_peso_limite=peso_tratta,
                        peso_accumulato=peso_accumulato + peso_tratta
                    )

                    parziale.pop()  # 3. UNDO: Tolgo il team per ripristinare lo stato e testare altre diramazioni