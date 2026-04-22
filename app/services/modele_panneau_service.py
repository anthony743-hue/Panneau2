from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import session_scope
from app.exceptions import ModelePanneauPersistenceError


def save_modele_panneau_payload(payload):
    try:
        with session_scope() as session:
            modele = payload["modele"]
            session.add(modele)
            session.flush()

            for configuration in payload.get("configurations_ensoleillement", []):
                configuration.modele_id = modele.id
                session.add(configuration)

            for configuration in payload.get("configurations_prix", []):
                configuration.modele_id = modele.id
                session.add(configuration)

            session.flush()
            return modele.id
    except ValueError:
        raise
    except IntegrityError as exc:
        raise ModelePanneauPersistenceError(
            "Impossible d'ajouter le modele en base a cause d'une contrainte SQL."
        ) from exc
    except SQLAlchemyError as exc:
        raise ModelePanneauPersistenceError(
            "Erreur SQLAlchemy lors de l'ajout du modele en base."
        ) from exc
