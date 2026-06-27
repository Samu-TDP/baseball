from dataclasses import dataclass

@dataclass
class Team:
    """
    Rappresenta l'entità Squadra con i 20 attributi esatti del database, disposti
    nell'ordine corretto richiesto per la mappatura.
    Ogni oggetto istanziato fungerà da Vertice (Nodo) del grafo completo.
    """

    year: int                # Anno del campionato di baseball (es: 1985)
    teamCode: str            # Codice/Sigla alfanumerica abbreviata del team (es: 'BOS')
    name: str                # Nome completo ed esteso ufficiale della squadra (es: 'Boston Red Sox')


    def __eq__(self, other):
        """
        Uguaglianza logica per NetworkX: due squadre sono lo stesso identico nodo
        se e solo se condividono lo stesso codice teamCode nello stesso anno.
        """
        if not isinstance(other, Team):
            return False
        return self.teamCode == other.teamCode and self.year == other.year

    def __hash__(self):
        """
        Calcola l'hash sulla chiave composta (teamCode, year) per inserire e cercare
        i nodi all'interno dei Set e delle idMap in un millisecondo.
        """
        return hash((self.teamCode, self.year))

    def __str__(self):
        """Rappresentazione testuale per l'interfaccia utente grafica."""
        return f"{self.teamCode} - {self.name}"