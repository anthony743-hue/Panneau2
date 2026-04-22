import tkinter as tk
from tkinter import ttk


class AppareilFormView:
    def __init__(self, root, tranches):
        self.root = root
        self.tranches = tranches
        self.current_page = None

        self.libelle_var = tk.StringVar()
        self.puissance_var = tk.StringVar()
        self.debut_var = tk.StringVar()
        self.fin_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Ajoute des appareils puis passe a la page de resultats."
        )
        self.results_status_var = tk.StringVar(
            value="Selectionne un ou plusieurs modeles pour afficher les resultats."
        )

        self.root.title("Dimensionnement Solaire ETU003919")
        self.root.geometry("1100x680")
        self._build_layout()

    def bind_controller(self, controller):
        self.tranche_listbox.bind("<<ListboxSelect>>", controller._sync_selected_tranche)
        self.modele_listbox.bind("<<ListboxSelect>>", controller._update_results_view)
        
        self.add_appareil_button.configure(command=controller._add_appareil)
        self.remove_selection_button.configure(command=controller._remove_selected)
        self.go_to_results_button.configure(command=controller._go_to_results_page)
        self.open_modele_form_button.configure(command=controller._open_modele_form)
        self.go_to_form_button.configure(command=controller._go_to_form_page)
        self.add_modele_button.configure(command=controller._open_modele_form)
        self.refresh_modele_button.configure(command=controller._refresh_modele_listbox)

    def show_page(self, page):
        self.current_page = page
        page.tkraise()

    def select_default_tranche(self):
        if not self.tranches:
            return

        self.tranche_listbox.selection_clear(0, tk.END)
        self.tranche_listbox.selection_set(0)
        self.tranche_listbox.activate(0)

    def set_results_text(self, text):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")

    def _build_layout(self):
        self.container = ttk.Frame(self.root, padding=16)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.form_page = ttk.Frame(self.container)
        self.form_page.grid(row=0, column=0, sticky="nsew")
        self.form_page.rowconfigure(1, weight=1)
        self.form_page.columnconfigure(0, weight=1)

        self.results_page = ttk.Frame(self.container)
        self.results_page.grid(row=0, column=0, sticky="nsew")
        self.results_page.rowconfigure(0, weight=1)
        self.results_page.columnconfigure(1, weight=1)

        self._build_form_page()
        self._build_results_page()

    def _build_form_page(self):
        form = ttk.LabelFrame(self.form_page, text="Ajouter un appareil", padding=12)
        form.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        ttk.Label(form, text="Libelle").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.libelle_var, width=26).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=4,
            pady=4,
        )

        ttk.Label(form, text="Puissance (W)").grid(
            row=0,
            column=2,
            sticky="w",
            padx=4,
            pady=4,
        )
        ttk.Entry(form, textvariable=self.puissance_var, width=18).grid(
            row=0,
            column=3,
            sticky="ew",
            padx=4,
            pady=4,
        )

        ttk.Label(form, text="Debut").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.debut_var, width=26).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=4,
            pady=4,
        )

        ttk.Label(form, text="Fin").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.fin_var, width=18).grid(
            row=1,
            column=3,
            sticky="ew",
            padx=4,
            pady=4,
        )

        tranche_frame = ttk.LabelFrame(form, text="TrancheHeure", padding=8)
        tranche_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=4, pady=(8, 4))
        tranche_frame.columnconfigure(0, weight=1)

        self.tranche_listbox = tk.Listbox(tranche_frame, height=4, exportselection=False)
        self.tranche_listbox.grid(row=0, column=0, sticky="ew")

        tranche_scrollbar = ttk.Scrollbar(
            tranche_frame,
            orient=tk.VERTICAL,
            command=self.tranche_listbox.yview,
        )
        tranche_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tranche_listbox.configure(yscrollcommand=tranche_scrollbar.set)

        for tranche in self.tranches:
            label = f"{tranche.libelle} ({tranche.debut:%H:%M:%S} - {tranche.fin:%H:%M:%S})"
            self.tranche_listbox.insert(tk.END, label)

        actions = ttk.Frame(form)
        actions.grid(row=3, column=0, columnspan=4, sticky="w", padx=4, pady=(8, 2))

        self.add_appareil_button = ttk.Button(actions, text="Ajouter appareil")
        self.add_appareil_button.pack(side=tk.LEFT, padx=(0, 8))

        self.remove_selection_button = ttk.Button(actions, text="Supprimer selection")
        self.remove_selection_button.pack(side=tk.LEFT)

        table_frame = ttk.LabelFrame(self.form_page, text="Appareils ajoutes", padding=12)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=8)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("libelle", "puissance", "tranche", "debut", "fin")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("libelle", text="Libelle")
        self.tree.heading("puissance", text="Puissance (W)")
        self.tree.heading("tranche", text="Tranche")
        self.tree.heading("debut", text="Debut")
        self.tree.heading("fin", text="Fin")
        self.tree.column("libelle", width=220)
        self.tree.column("puissance", width=130, anchor="center")
        self.tree.column("tranche", width=150, anchor="center")
        self.tree.column("debut", width=120, anchor="center")
        self.tree.column("fin", width=120, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        bottom = ttk.Frame(self.form_page)
        bottom.grid(row=2, column=0, sticky="ew", padx=4, pady=4)

        self.go_to_results_button = ttk.Button(
            bottom,
            text="Continuer vers les resultats",
        )
        self.go_to_results_button.pack(side=tk.LEFT, padx=(0, 8))

        self.open_modele_form_button = ttk.Button(
            bottom,
            text="Ajouter modele de panneau",
        )
        self.open_modele_form_button.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT, padx=8)

    def _build_results_page(self):
        left = ttk.LabelFrame(self.results_page, text="Choix des modeles", padding=12)
        left.grid(row=0, column=0, sticky="nsw", padx=(4, 8), pady=4)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        ttk.Label(
            left,
            text=(
                "Selection multiple autorisee. "
                "Les resultats se recalculent a chaque selection."
            ),
            wraplength=240,
            justify=tk.LEFT,
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.modele_listbox = tk.Listbox(
            left,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            width=34,
        )
        self.modele_listbox.grid(row=1, column=0, sticky="nsew")

        modele_scrollbar = ttk.Scrollbar(
            left,
            orient=tk.VERTICAL,
            command=self.modele_listbox.yview,
        )
        modele_scrollbar.grid(row=1, column=1, sticky="ns")
        self.modele_listbox.configure(yscrollcommand=modele_scrollbar.set)

        left_actions = ttk.Frame(left)
        left_actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self.go_to_form_button = ttk.Button(left_actions, text="Retour appareils")
        self.go_to_form_button.pack(side=tk.LEFT, padx=(0, 8))

        self.add_modele_button = ttk.Button(left_actions, text="Ajouter modele")
        self.add_modele_button.pack(side=tk.LEFT, padx=(0, 8))

        self.refresh_modele_button = ttk.Button(left_actions, text="Actualiser")
        self.refresh_modele_button.pack(side=tk.LEFT)

        right = ttk.LabelFrame(self.results_page, text="Resultats", padding=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 4), pady=4)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, textvariable=self.results_status_var).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        self.results_text = tk.Text(right, wrap="word", state="disabled")
        self.results_text.grid(row=1, column=0, sticky="nsew")

        results_scrollbar = ttk.Scrollbar(
            right,
            orient=tk.VERTICAL,
            command=self.results_text.yview,
        )
        results_scrollbar.grid(row=1, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
