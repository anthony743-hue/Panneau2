from datetime import time

from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import relationship

from app.database import Base


class TrancheHeure(Base):
    __tablename__ = "TrancheHeure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    _libelle = Column("libelle", String(120), nullable=False)
    _debut = Column("heure_debut", Time, nullable=False)
    _fin = Column("heure_fin", Time, nullable=False)

    # relation inverse
    configurations = relationship("ConfigurationPanneauByTranche", back_populates="tranche_heure")

    def __init__(self, libelle=None, debut=None, fin=None):
        self._libelle = libelle
        self._debut = debut
        self._fin = fin

    # 🔹 Property libelle
    @property
    def libelle(self):
        return self._libelle

    @libelle.setter
    def libelle(self, value):
        if not value:
            raise ValueError("Le libellé ne peut pas être vide")
        self._libelle = value

    # 🔹 Property debut
    @property
    def debut(self):
        return self._debut

    @debut.setter
    def debut(self, value):
        if not isinstance(value, time):
            raise TypeError("debut doit être de type datetime.time")
        self._debut = value

    # 🔹 Property fin
    @property
    def fin(self):
        return self._fin

    @fin.setter
    def fin(self, value):
        if not isinstance(value, time):
            raise TypeError("fin doit être de type datetime.time")
        self._fin = value

    @staticmethod
    def as_hour(value):
        if isinstance(value, time):
            return value.hour
        if isinstance(value, int):
            return value % 24
        raise ValueError("Heure invalide.")

    def get_heures(self):
        debut = self.as_hour(self.debut)
        fin = self.as_hour(self.fin)
        if debut < fin:
            return list(range(debut, fin))
        return list(range(debut, 24)) + list(range(0, fin))

    def contains_time(self, value):
        if value == self.debut or value == self.fin:
            return True
        return self.as_hour(value) in self.get_heures()

    def format_interval(self, fmt="%H:%M:%S"):
        return f"{self.debut.strftime(fmt)} - {self.fin.strftime(fmt)}"

    def __str__(self):
        return f"TrancheHeure(libelle={self._libelle}, debut={self._debut}, fin={self._fin})"

    def __repr__(self):
        return f"<TrancheHeure(id={self.id}, libelle='{self._libelle}')>"
