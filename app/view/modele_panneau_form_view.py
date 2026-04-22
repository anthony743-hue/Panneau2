import tkinter as tk
from tkinter import ttk


class ModelePanneauFormView(tk.Toplevel):
    def __init__(self, master=None, tranches=None):
        super().__init__(master)
        self.tranches = tranches or []
        self.form_vars = {}
        self.nom_var = tk.StringVar()
        self.prix_jour_ouvrable_var = tk.StringVar(value="0")
        self.prix_jour_non_ouvrable_var = tk.StringVar(value="0")
        self.result_var = tk.StringVar(value="Aucun modele ajoute pour l'instant.")

        self.title("Ajouter un modele de panneau")
        self.geometry("980x620")
        self.transient(master)
        self._build_layout()

    def bind_controller(self, controller):
        self.add_model_button.configure(command=controller._add_model)
        self.reset_form_button.configure(command=controller._reset_form)

    def _build_layout(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)

        form = ttk.LabelFrame(container, text="Nouveau modele", padding=12)
        form.grid(row=0, column=0, sticky="nsew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Nom du modele").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.nom_var, width=30).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=4,
            pady=4,
        )

        ttk.Label(form, text="Prix jour ouvrable").grid(
            row=1,
            column=0,
            sticky="w",
            padx=4,
            pady=4,
        )
        ttk.Entry(form, textvariable=self.prix_jour_ouvrable_var, width=30).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=4,
            pady=4,
        )

        ttk.Label(form, text="Prix jour non ouvrable").grid(
            row=2,
            column=0,
            sticky="w",
            padx=4,
            pady=4,
        )
        ttk.Entry(form, textvariable=self.prix_jour_non_ouvrable_var, width=30).grid(
            row=2,
            column=1,
            sticky="ew",
            padx=4,
            pady=4,
        )

        grid_frame = ttk.Frame(form)
        grid_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(12, 4))
        for col in range(2):
            grid_frame.columnconfigure(col, weight=1)

        headers = (
            "Tranche",
            "Ensoleillement (%)",
        )
        for col, title in enumerate(headers):
            ttk.Label(grid_frame, text=title).grid(row=0, column=col, sticky="w", padx=4, pady=4)

        for row, tranche in enumerate(self.tranches, start=1):
            ensoleillement_var = tk.StringVar(value="0")

            self.form_vars[tranche.id] = {
                "tranche": tranche,
                "ensoleillement": ensoleillement_var,
            }

            ttk.Label(
                grid_frame,
                text=f"{tranche.libelle} ({tranche.debut:%H:%M} - {tranche.fin:%H:%M})",
            ).grid(row=row, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(grid_frame, textvariable=ensoleillement_var, width=18).grid(
                row=row,
                column=1,
                sticky="ew",
                padx=4,
                pady=4,
            )

        actions = ttk.Frame(form)
        actions.grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=(12, 4))

        self.add_model_button = ttk.Button(actions, text="Ajouter modele")
        self.add_model_button.pack(side=tk.LEFT, padx=(0, 8))

        self.reset_form_button = ttk.Button(actions, text="Reinitialiser")
        self.reset_form_button.pack(side=tk.LEFT)

        summary = ttk.LabelFrame(container, text="Modeles disponibles", padding=12)
        summary.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        summary.columnconfigure(0, weight=1)
        summary.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        columns = ("index", "nom", "tranches", "prix")
        self.tree = ttk.Treeview(summary, columns=columns, show="headings", height=10)
        self.tree.heading("index", text="Ref")
        self.tree.heading("nom", text="Modele")
        self.tree.heading("tranches", text="Tranches configurees")
        self.tree.heading("prix", text="Configs prix")
        self.tree.column("index", width=60, anchor="center")
        self.tree.column("nom", width=260)
        self.tree.column("tranches", width=170, anchor="center")
        self.tree.column("prix", width=150, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(summary, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        ttk.Label(summary, textvariable=self.result_var).grid(row=1, column=0, sticky="w", pady=(10, 0))
