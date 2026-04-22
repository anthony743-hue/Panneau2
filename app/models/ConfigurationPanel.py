from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class ConfigurationPanneauByTranche(Base):
    __tablename__ = "ConfigurationPanneauByTranche"

    id = Column(Integer, primary_key=True, autoincrement=True)
    _id_tranche_heure = Column("id_tranche_heure", Integer, ForeignKey("TrancheHeure.id"), nullable=False)
    _pourcentage_ensoleillement = Column("pourcentage_ensoleillement", Float, nullable=False)
    _modele_id = Column("modele_id", Integer, ForeignKey("modelePanneau.id"), nullable=False)

    tranche_heure = relationship("TrancheHeure", back_populates="configurations")
    modele = relationship("ModelePanneau", back_populates="configurations_ensoleillement")

    def __init__(self, id_tranche_heure=None, pourcentage_ensoleillement=0.0, modele_id=None):
        self._id_tranche_heure = id_tranche_heure
        self._pourcentage_ensoleillement = pourcentage_ensoleillement
        self._modele_id = modele_id

    # 🔹 Property pour id_tranche_heure
    @property
    def id_tranche_heure(self):
        return self._id_tranche_heure

    @id_tranche_heure.setter
    def id_tranche_heure(self, value):
        self._id_tranche_heure = value

    # 🔹 Property pour pourcentage_ensoleillement
    @property
    def pourcentage_ensoleillement(self):
        return self._pourcentage_ensoleillement

    @pourcentage_ensoleillement.setter
    def pourcentage_ensoleillement(self, value):
        self._pourcentage_ensoleillement = value

    @property
    def modele_id(self):
        return self._modele_id

    @modele_id.setter
    def modele_id(self, value):
        self._modele_id = value

    def resolve_tranche(self, tranches=None):
        if self.tranche_heure is not None:
            return self.tranche_heure
        if tranches is None:
            return None
        for tranche in tranches:
            if tranche.id == self.id_tranche_heure:
                return tranche
        return None

    def to_percent_config_entry(self, tranches=None):
        tranche = self.resolve_tranche(tranches=tranches)
        if tranche is None:
            return None
        return tranche.libelle, self.pourcentage_ensoleillement

    def __str__(self):
        return (f"ConfigurationPanneauByTranche("
                f"tranche_id={self._id_tranche_heure}, "
                f"ensoleillement={self._pourcentage_ensoleillement}, "
                f"modele_id={self._modele_id})")

    def __repr__(self):
        return (f"<Configuration(id={self.id}, "
                f"tranche_id={self._id_tranche_heure}, "
                f"ensoleillement={self._pourcentage_ensoleillement}, "
                f"modele_id={self._modele_id})>")
