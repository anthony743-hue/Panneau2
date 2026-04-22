from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base, session_scope


class ConfigurationPrixPanneau(Base):
    __tablename__ = "ConfigurationPrixPanneau"

    id = Column(Integer, primary_key=True, autoincrement=True)
    _modele_id = Column("modele_id", Integer, ForeignKey("modelePanneau.id"), nullable=False)
    _prix_jour_ouvrable = Column("prix_jour_ouvrable", Integer, nullable=False, default=0)
    _prix_jour_non_ouvrable = Column(
        "prix_jour_non_ouvrable",
        Integer,
        nullable=False,
        default=0,
    )

    modele = relationship("ModelePanneau", back_populates="configurations_prix")

    def __init__(self,modele_id=None,prix_jour_ouvrable=0,prix_jour_non_ouvrable=0):
        self._modele_id = modele_id
        self.prix_jour_ouvrable = prix_jour_ouvrable
        self.prix_jour_non_ouvrable = prix_jour_non_ouvrable

    @property
    def modele_id(self):
        return self._modele_id

    @modele_id.setter
    def modele_id(self, value):
        self._modele_id = value

    @property
    def prix_jour_ouvrable(self):
        return self._prix_jour_ouvrable

    @prix_jour_ouvrable.setter
    def prix_jour_ouvrable(self, value):
        if value is None or value < 0:
            raise ValueError("Le prix jour ouvrable doit etre un entier >= 0.")
        self._prix_jour_ouvrable = int(value)

    @property
    def prix_jour_non_ouvrable(self):
        return self._prix_jour_non_ouvrable

    @prix_jour_non_ouvrable.setter
    def prix_jour_non_ouvrable(self, value):
        if value is None or value < 0:
            raise ValueError("Le prix jour non ouvrable doit etre un entier >= 0.")
        self._prix_jour_non_ouvrable = int(value)

    def to_price_config(self):
        return {
            0: self.prix_jour_ouvrable,
            1: self.prix_jour_non_ouvrable,
        }

    @staticmethod
    def getAll():
        try:
            with session_scope() as session:
                arr = session.query(ConfigurationPrixPanneau).all()
                for a in arr:
                    print(a.to_price_config()) 
                return { a.modele_id: a.to_price_config() for a in arr }
        except Exception as exc:
            raise ValueError(
                "Erreur lors de la recuperation des modeles de panneau depuis la base."
            ) from exc
    def __repr__(self):
        return (
            f"<ConfigurationPrixPanneau(id={self.id}, "
            f"modele_id={self._modele_id}, "
            f"prix_jour_ouvrable={self._prix_jour_ouvrable}, "
            f"prix_jour_non_ouvrable={self._prix_jour_non_ouvrable})>"
        )
