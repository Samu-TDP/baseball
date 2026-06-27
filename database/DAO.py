from database.DB_connect import DBConnect
from model.team import Team


class DAO():
    def __init__(self):
        pass

    # =========================================================================
    # QUERY 1: CARICAMENTO TENDINA ANNI (Inizializzazione)
    # =========================================================================
    @staticmethod
    def getAllYears():
        """
        ESTRAPOLAZIONE: Isola gli anni di campionato unici a partire dal 1980.
        MODALITÀ: Applica DISTINCT sulla colonna 'year' per evitare anni duplicati.
        STRUTTURA DATI: Salva i dati in una 'list' di numeri interi (list of int).
        """
        conn = DBConnect.get_connection()
        results = []
        cursor = conn.cursor(dictionary=True)

        query = """SELECT DISTINCT(t.year)
                   FROM teams t
                   WHERE t.year >= 1980
                   ORDER BY t.year DESC"""

        cursor.execute(query)
        for row in cursor:
            results.append(int(row["year"]))

        cursor.close()
        conn.close()
        return results

    # =========================================================================
    # QUERY 2: ANAGRAFICA GLOBALE DI TUTTE SQUADRE (Identity Map Boot)
    # =========================================================================
    @staticmethod
    def getAllTeams():
        """
        ESTRAPOLAZIONE: Scarica l'anagrafica storica essenziale delle squadre.
        MODALITÀ: Estrae l'anno, il codice e il nome per popolare la mappa d'identità in RAM.
        STRUTTURA DATI: Salva i dati in una 'list' di oggetti modello 'Team'.
        """
        conn = DBConnect.get_connection()
        results = []
        cursor = conn.cursor(dictionary=True)

        query = "SELECT t.year, t.teamCode, t.name FROM teams t"

        cursor.execute(query)
        for row in cursor:
            results.append(Team(**row))

        cursor.close()
        conn.close()
        return results

    # =========================================================================
    # QUERY 3: ESTRAZIONE VERTICI UNICI (Nodi del Grafo)
    # =========================================================================
    @staticmethod
    def getAllNodes(anno, id_map_teams):
        """
        ESTRAPOLAZIONE: Rileva i codici delle squadre che hanno giocato nell'anno scelto.
        MODALITÀ: Usa DISTINCT su 'teamCode' per comprimere i duplicati strutturali del DB.
        STRUTTURA DATI: Converte i codici unici negli oggetti stabili presi dalla mappa
        d'identità, restituendo una 'list' di oggetti 'Team' unici per istanza.
        """
        conn = DBConnect.get_connection()
        results = []
        cursor = conn.cursor(dictionary=True)

        query = """SELECT DISTINCT t.teamCode
                   FROM teams t
                   WHERE t.year = %s"""

        cursor.execute(query, (anno,))
        for row in cursor:
            codice_squadra = row["teamCode"]
            # Sfruttiamo la id_map per recuperare l'oggetto unico condiviso in memoria RAM
            if codice_squadra in id_map_teams:
                results.append(id_map_teams[codice_squadra])

        cursor.close()
        conn.close()
        return results

    # =========================================================================
    # QUERY 4: BUDGET SALARIALI AGGREGATI (Pesi degli Archi)
    # =========================================================================
    @staticmethod
    def getSalariSquadre(anno):
        """
        ESTRAPOLAZIONE: Calcola il budget totale dei salari erogato da ogni club nell'anno.
        MODALITÀ: Filtra per l'anno, raggruppa per 'teamCode' e calcola la somma con SUM(s.salary).
        STRUTTURA DATI: Un dizionario (dict) Python mappato come { 'ARI': 45000000.0 }.
        Garantisce al Model una consultazione immediata in tempo costante O(1).
        """
        conn = DBConnect.get_connection()
        results = {}
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT s.teamCode AS teamCode, SUM(s.salary) AS salarioTotale
            FROM salaries s
            WHERE s.year = %s
            GROUP BY s.teamCode
        """

        cursor.execute(query, (anno,))
        for row in cursor:
            results[row["teamCode"]] = float(row["salarioTotale"])

        cursor.close()
        conn.close()
        return results