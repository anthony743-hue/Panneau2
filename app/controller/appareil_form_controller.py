from datetime import datetime, time
from tkinter import messagebox

from app.entity.Appareil import Appareil
from app.utils import (
    getResult,
    get_default_tranches,
    get_heures_tranche,
    get_modele_panneau_payloads,
)
from app.view.appareil_form_view import AppareilFormView
from app.view.modele_panneau_form import open_modele_panneau_form


class AppareilFormController:
    def __init__(self, root):
        self.root = root
        self.appareils = []
        self.modeles_panneau = get_modele_panneau_payloads()
        self.tranches = get_default_tranches()
        self.tranches_by_id = {tranche.id: tranche for tranche in self.tranches}

        self.view = AppareilFormView(root=root, tranches=self.tranches)
        self.view.bind_controller(self)
        self._select_default_tranche()
        self.view.show_page(self.view.form_page)

    def _show_page(self, page):
        self.view.show_page(page)

    def _select_default_tranche(self):
        self.view.select_default_tranche()
        self._sync_selected_tranche()

    def _sync_selected_tranche(self, _event=None):
        tranche = self._get_selected_tranche()
        if tranche is None:
            self.view.debut_var.set("")
            self.view.fin_var.set("")
            return

        self.view.debut_var.set(self._format_time(tranche.debut))
        self.view.fin_var.set(self._format_time(tranche.fin))

    def _get_selected_tranche(self):
        selection = self.view.tranche_listbox.curselection()
        if not selection:
            return None
        return self.tranches[selection[0]]

    def _coerce_time(self, value):
        if isinstance(value, time):
            return value
        if isinstance(value, int):
            return time(value % 24, 0)
        raise ValueError("Valeur d'heure invalide.")

    def _format_time(self, value):
        return self._coerce_time(value).strftime("%H:%M:%S")

    def _format_tranche_label(self, tranche):
        return (
            f"{tranche.libelle} "
            f"({self._format_time(tranche.debut)} - {self._format_time(tranche.fin)})"
        )

    def _parse_time(self, raw):
        value = raw.strip()
        formats = ("%H:%M:%S", "%H:%M", "%H")
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                pass
        raise ValueError("Format heure invalide. Utilise HH:MM ou HH:MM:SS.")

    def _is_time_in_tranche(self, value, tranche):
        tranche_debut = self._coerce_time(tranche.debut)
        tranche_fin = self._coerce_time(tranche.fin)

        if value == tranche_debut or value == tranche_fin:
            return True

        return value.hour in get_heures_tranche(tranche)

    def _validate_time_in_tranche(self, label, value, tranche):
        if not self._is_time_in_tranche(value, tranche):
            raise ValueError(
                f"{label} doit rester dans la tranche {tranche.libelle} "
                f"({self._format_time(tranche.debut)} - {self._format_time(tranche.fin)})."
            )

    def _insert_appareil_row(self, index, appareil):
        tranche = self.tranches_by_id.get(appareil.tranche)
        tranche_label = tranche.libelle if tranche is not None else str(appareil.tranche)
        self.view.tree.insert(
            "",
            "end",
            iid=str(index),
            values=(
                appareil.libelle,
                f"{appareil.puissance:.2f}",
                tranche_label,
                appareil.debut.strftime("%H:%M:%S"),
                appareil.fin.strftime("%H:%M:%S"),
            ),
        )

    def _refresh_appareils_tree(self):
        for row in self.view.tree.get_children():
            self.view.tree.delete(row)

        for idx, appareil in enumerate(self.appareils):
            self._insert_appareil_row(idx, appareil)

    def _add_appareil(self):
        try:
            libelle = self.view.libelle_var.get().strip()
            puissance = float(self.view.puissance_var.get().strip())
            tranche = self._get_selected_tranche()
            if tranche is None:
                raise ValueError("Selectionne une tranche horaire.")
            debut = self._parse_time(self.view.debut_var.get())
            fin = self._parse_time(self.view.fin_var.get())
            self._validate_time_in_tranche("Debut", debut, tranche)
            self._validate_time_in_tranche("Fin", fin, tranche)

            appareil = Appareil()
            appareil.libelle = libelle
            appareil.puissance = puissance
            appareil.debut = debut
            appareil.fin = fin
            appareil.tranche = tranche.id
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Erreur de saisie", str(exc))
            return

        self.appareils.append(appareil)
        self._insert_appareil_row(len(self.appareils) - 1, appareil)

        self.view.libelle_var.set("")
        self.view.puissance_var.set("")
        self._update_status()

    def _remove_selected(self):
        selected = self.view.tree.selection()
        if not selected:
            return

        for item_id in selected:
            index = int(item_id)
            self.appareils[index] = None
            self.view.tree.delete(item_id)

        self.appareils = [appareil for appareil in self.appareils if appareil is not None]
        self._refresh_appareils_tree()
        self._update_status()

    def _go_to_results_page(self):
        if not self.appareils:
            messagebox.showwarning(
                "Aucun appareil",
                "Ajoute au moins un appareil avant de continuer.",
            )
            return

        self._refresh_modele_listbox()
        self._show_page(self.view.results_page)
        self._update_results_view()

    def _go_to_form_page(self):
        self._show_page(self.view.form_page)
        self._update_status()

    def _refresh_modele_listbox(self):
        previous_selection = {
            payload["modele"].id for payload in self._get_selected_modele_payloads()
        }

        self.view.modele_listbox.delete(0, "end")
        for index, payload in enumerate(self.modeles_panneau):
            modele = payload["modele"]
            label = f"{modele.id} - {modele.nom}"
            self.view.modele_listbox.insert("end", label)
            if modele.id in previous_selection:
                self.view.modele_listbox.selection_set(index)

        if not self.modeles_panneau:
            self.view.results_status_var.set(
                "Aucun modele disponible. Ajoute d'abord un modele de panneau."
            )
        else:
            self.view.results_status_var.set(
                "Selectionne un ou plusieurs modeles pour afficher les resultats."
            )

    def _get_selected_modele_payloads(self):
        selected = self.view.modele_listbox.curselection()
        return [
            self.modeles_panneau[index]
            for index in selected
            if index < len(self.modeles_panneau)
        ]

    def _update_results_view(self, _event=None):
        if not self.appareils:
            self.view.results_status_var.set("Aucun appareil disponible.")
            self.view.set_results_text("")
            return

        if not self.modeles_panneau:
            self.view.results_status_var.set(
                "Aucun modele disponible. Ajoute d'abord un modele de panneau."
            )
            self.view.set_results_text("")
            return

        payloads = self._get_selected_modele_payloads()
        if not payloads:
            self.view.results_status_var.set("Selectionne au moins un modele a gauche.")
            self.view.set_results_text("")
            return

        modele_ids = [payload["modele"].id for payload in payloads]

        try:
            results = getResult(
                appareils=self.appareils,
                modele_id=modele_ids,
                modeles_data=self.modeles_panneau,
            )
        except ValueError as exc:
            messagebox.showerror("Erreur", str(exc))
            return

        blocks = []
        for payload, result in zip(payloads, results):
            blocks.append(self._format_result_block(payload["modele"], result))

        self.view.results_status_var.set(
            f"{len(payloads)} modele(s) selectionne(s) pour "
            f"{len(self.appareils)} appareil(s)."
        )
        self.view.set_results_text("\n\n".join(blocks))

    def _format_result_block(self, modele, result):
        unused_energy = ", ".join(
            f"{heure:02d}h={value:.2f} Wh"
            for heure, value in sorted(result.get("energy_not_working", {}).items())
        )
        if not unused_energy:
            unused_energy = "Aucune"

        return (
            f"Modele {modele.id} - {modele.nom}\n"
            f"Puissance panneau: {result['puissance_panneau_minimale']:.2f} W\n"
            f"puissance_panneau_minimale_reel : {result['puissance_panneau_minimale_reel']:.2f} \n"
            f"batterie_pratique: {result['batterie_pratique']:.2f} Wh\n"
            f"Charge batterie: {result['charge_batterie']:.2f} Wh\n"
            f"Energie non utilisee par heure: {result['total_energy_unused']:.2f} Wh\n"
            f"Prix Energie non utilisee pendant un jour ouvrable: {result['prix_enerige_ouvrable']:.2f} Ar\n"
            f"Prix Energie non utilisee pendant un jour non ouvrable: {result['prix_enerige_non_ouvrable']:.2f} Ar\n"
        )

    def _update_status(self):
        self.view.status_var.set(
            f"{len(self.appareils)} appareil(s) ajoutes | "
            f"{len(self.modeles_panneau)} modele(s) disponibles."
        )

    def _open_modele_form(self):
        window = open_modele_panneau_form(
            master=self.root,
            modeles_store=self.modeles_panneau,
        )
        self.root.wait_window(window)
        self._update_status()
        self._refresh_modele_listbox()
        if self.view.current_page is self.view.results_page:
            self._update_results_view()
