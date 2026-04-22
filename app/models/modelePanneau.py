from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.orm import relationship

from app.database import Base


class ModelePanneau(Base):
    __tablename__ = "modelePanneau"

    id = Column(Integer, primary_key=True, autoincrement=True)

    _nom = Column("nom", Unicode(100), nullable=False)

    configurations_ensoleillement = relationship(
        "ConfigurationPanneauByTranche",
        back_populates="modele",
    )
    configurations_prix = relationship(
        "ConfigurationPrixPanneau",
        back_populates="modele",
    )

    def __init__(self, nom):
        self.nom = nom

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, value):
        if value is None or not value.strip():
            raise ValueError("Le nom du modele ne peut pas etre vide.")
        self._nom = value.strip()

    def matches_id(self, modele_id):
        return self.id == modele_id

    def build_percent_config(self, tranches=None, configurations=None):
        config = {}
        items = (
            configurations
            if configurations is not None
            else list(self.configurations_ensoleillement)
        )
        for item in items:
            entry = item.to_percent_config_entry(tranches=tranches)
            if entry is None:
                continue
            libelle, pourcentage = entry
            config[libelle] = pourcentage
        return config

    def build_price_config(self, configurations=None):
        config = {}
        items = (
            configurations
            if configurations is not None
            else list(self.configurations_prix)
        )
        for item in items:
            config.update(item.to_price_config())
        return config

    def to_payload(self):
        return {
            "modele": self,
            "configurations_ensoleillement": list(self.configurations_ensoleillement),
            "configurations_prix": list(self.configurations_prix),
        }

    def __repr__(self):
        return f"<ModelePanneau(id={self.id}, nom='{self._nom}')>"
