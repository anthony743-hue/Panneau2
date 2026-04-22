from datetime import time

class Appareil:
    def __init__(self, libelle=None, puissance=0, debut=None, fin=None,tranche=-1):
        self._libelle = libelle
        self._puissance = puissance
        self._debut = debut
        self._fin = fin
        self._tranche = tranche

    # 🔹 libelle
    @property
    def libelle(self):
        return self._libelle

    @libelle.setter
    def libelle(self, value):
        if value is None or value.strip() == "":
            raise ValueError("Le libellé ne peut pas être vide.")
        self._libelle = value

    # 🔹 puissance
    @property
    def puissance(self):
        return self._puissance

    @puissance.setter
    def puissance(self, value):
        if value < 0:
            raise ValueError("La puissance ne peut pas être négative.")
        self._puissance = value

    # 🔹 debut
    @property
    def debut(self) -> time:
        return self._debut

    @debut.setter
    def debut(self, value):
        if value is None:
            raise ValueError("Le début ne peut pas être vide.")
        if not isinstance(value, time):
            raise TypeError("Le début doit être de type datetime.time")
        self._debut = value

    # 🔹 fin
    @property
    def fin(self) -> time:
        return self._fin

    @fin.setter
    def fin(self, value):
        if value is None:
            raise ValueError("La fin ne peut pas être vide.")
        if not isinstance(value, time):
            raise TypeError("La fin doit être de type datetime.time")
        self._fin = value

    @property
    def tranche(self) -> int:
        return self._tranche

    @tranche.setter
    def tranche(self, value):
        if value is None or value <= 0:
            raise ValueError("Le tranche ne peut pas avoir de valeur vide")
        self._tranche = value

    def __str__(self):
        return (f"Appareil [Libellé: {self._libelle}, "
                f"Puissance: {self._puissance}W, "
                f"Début: {self._debut}, Fin: {self._fin}]")