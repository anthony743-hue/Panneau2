from sqlalchemy import Column, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, session_scope


class ConfigurationHeurePoint(Base):
    __tablename__ = "ConfigurationHeurePoint"

    id = Column(Integer, primary_key=True, autoincrement=True)
    debut = Column("heure_debut", Time, nullable=False)
    fin = Column("heure_fin", Time, nullable=False)
    pourcentage_ouvrable = Column("pourcentage_ouvrable", Integer, nullable=False, default=0)
    pourcentage_non_ouvrable = Column("pourcentage_non_ouvrable", Integer, nullable=False, default=0)
    modele_id = Column("modele_id", Integer, ForeignKey("modelePanneau.id"), nullable=False)

    @staticmethod
    def getAll():
        try:
            with session_scope() as session:
                arr = session.query(ConfigurationHeurePoint).all()
                
                ret = {}
                for a in arr:
                    print(a)
                    temp = ret.get(a.modele_id, [])
                    temp.append(a)
                return ret
        except Exception as exc:
             raise ValueError(
                "Erreur lors de la recuperation des modeles de ConfigurationHeurePoint depuis la base."
            ) from exc
        
    def get_percent(self, value):
        return value / 100
    
    def pourcentage_load(self):
        return self.get_percent(self.pourcentage_ouvrable) , self.get_percent(self.pourcentage_non_ouvrable)
    
    def contains_time(self, value):
        if value == self.debut or value == self.fin:
            return True
        return value in self.get_heures()
    
    def get_heures(self):
        debut = self.as_hour(self.debut)
        fin = self.as_hour(self.fin)
        if debut < fin:
            return list(range(debut, fin))
        return list(range(debut, 24)) + list(range(0, fin))