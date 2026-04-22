from tkinter import messagebox

from app.exceptions import ModelePanneauLoadError, ModelePanneauPersistenceError
from app.models.ConfigurationPanel import ConfigurationPanneauByTranche
from app.models.ConfigurationPrix import ConfigurationPrixPanneau
from app.models.modelePanneau import ModelePanneau
from app.services.modele_panneau_service import save_modele_panneau_payload
from app.utils import get_default_tranches, get_modele_panneau_payloads
from app.view.modele_panneau_form_view import ModelePanneauFormView


class ModelePanneauFormController:
    def __init__(self, master=None, modeles_store=None, tranches=None, view=None):
        self.modeles_store = (
            modeles_store
            if modeles_store is not None
            else get_modele_panneau_payloads()
        )
        self.tranches = tranches if tranches is not None else get_default_tranches()
        self.view = view or ModelePanneauFormView(master=master, tranches=self.tranches)
        self.view.bind_controller(self)
        self._refresh_models_table()

    def _parse_float(self, value, field_label, min_value=None, max_value=None):
        try:
            parsed = float(value.strip())
        except ValueError as exc:
            raise ValueError(f"{field_label} doit etre un nombre.") from exc

        if min_value is not None and parsed < min_value:
            raise ValueError(f"{field_label} doit etre >= {min_value}.")
        if max_value is not None and parsed > max_value:
            raise ValueError(f"{field_label} doit etre <= {max_value}.")
        return parsed

    def _parse_int(self, value, field_label, min_value=None, max_value=None):
        raw = value.strip()
        if not raw:
            raise ValueError(f"{field_label} doit etre un entier.")

        try:
            parsed = int(raw)
        except ValueError as exc:
            raise ValueError(f"{field_label} doit etre un entier.") from exc

        if min_value is not None and parsed < min_value:
            raise ValueError(f"{field_label} doit etre >= {min_value}.")
        if max_value is not None and parsed > max_value:
            raise ValueError(f"{field_label} doit etre <= {max_value}.")
        return parsed

    def _build_payload(self):
        modele = ModelePanneau(self.view.nom_var.get())
        configurations_ensoleillement = []
        prix_jour_ouvrable = self._parse_int(
            self.view.prix_jour_ouvrable_var.get(),
            "Prix jour ouvrable",
            min_value=0,
        )
        prix_jour_non_ouvrable = self._parse_int(
            self.view.prix_jour_non_ouvrable_var.get(),
            "Prix jour non ouvrable",
            min_value=0,
        )

        for values in self.view.form_vars.values():
            tranche = values["tranche"]
            ensoleillement = self._parse_float(
                values["ensoleillement"].get(),
                f"Ensoleillement pour {tranche.libelle}",
                min_value=0,
                max_value=100,
            )

            configuration_ensoleillement = ConfigurationPanneauByTranche(
                id_tranche_heure=tranche.id,
                pourcentage_ensoleillement=ensoleillement,
            )
            configuration_ensoleillement.modele = modele
            configurations_ensoleillement.append(configuration_ensoleillement)

        configuration_prix = ConfigurationPrixPanneau(
            prix_jour_ouvrable=prix_jour_ouvrable,
            prix_jour_non_ouvrable=prix_jour_non_ouvrable,
        )
        configuration_prix.modele = modele

        return {
            "modele": modele,
            "configurations_ensoleillement": configurations_ensoleillement,
            "configurations_prix": [configuration_prix],
        }

    def _add_model(self):
        try:
            payload = self._build_payload()
            save_modele_panneau_payload(payload)
            self._reload_modeles_store()
        except (ModelePanneauPersistenceError, ModelePanneauLoadError, ValueError) as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.view)
            return

        self._refresh_models_table()
        self._reset_form()
        self.view.result_var.set(
            f"{len(self.modeles_store)} modele(s) charges depuis la base de donnees."
        )

    def _refresh_models_table(self):
        for item_id in self.view.tree.get_children():
            self.view.tree.delete(item_id)

        for index, payload in enumerate(self.modeles_store, start=1):
            self.view.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    index,
                    payload["modele"].nom,
                    len(payload["configurations_ensoleillement"]),
                    len(payload["configurations_prix"]),
                ),
            )

    def _reset_form(self):
        self.view.nom_var.set("")
        self.view.prix_jour_ouvrable_var.set("0")
        self.view.prix_jour_non_ouvrable_var.set("0")
        for values in self.view.form_vars.values():
            values["ensoleillement"].set("0")

    def _reload_modeles_store(self):
        payloads = get_modele_panneau_payloads()
        self.modeles_store.clear()
        self.modeles_store.extend(payloads)
