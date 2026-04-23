# Exemple d'intégration dans AppareilFormController

## Modification proposée pour app/controller/appareil_form_controller.py

### 1. Ajouter à l'import:
```python
from app.utils import (
    getResult,
    get_default_tranches,
    get_heures_tranche,
    get_modele_panneau_payloads,
    import_appareils_from_csv,  # ← Nouvelle import
)
```

### 2. Ajouter une méthode au contrôleur:
```python
def import_appareils_from_csv_button_clicked(self):
    """Importe des appareils depuis un fichier CSV."""
    appareils = import_appareils_from_csv(self.root)
    
    if appareils:
        for appareil in appareils:
            self.appareils.append(appareil)
            index = len(self.appareils) - 1
            self._insert_appareil_row(index, appareil)
        
        messagebox.showinfo(
            "Succès",
            f"{len(appareils)} appareil(s) ajouté(s) avec succès!"
        )
```

### 3. Ajouter un bouton dans la vue (app/view/appareil_form_view.py):
```python
# Dans AppareilFormView.__init__()
self.import_csv_button = ttk.Button(
    button_frame,
    text="📥 Importer CSV",
    command=self._on_import_csv
)
self.import_csv_button.pack(side=tk.LEFT, padx=5, pady=5)

# Ajouter la méthode
def _on_import_csv(self):
    if self.controller:
        self.controller.import_appareils_from_csv_button_clicked()
```

### 4. Lier le contrôleur dans AppareilFormController:
```python
def bind_view_events(self):
    """Lie les événements de la vue au contrôleur."""
    self.view.import_csv_button.config(
        command=self.import_appareils_from_csv_button_clicked
    )
```

## Usage complet

### Exemple 1: Interface complète avec tkinter

```python
import tkinter as tk
from tkinter import ttk
from app.controller.appareil_form_controller import AppareilFormController

# Créer la fenêtre
root = tk.Tk()
root.title("Gestion des Appareils")

# Initialiser le contrôleur
controller = AppareilFormController(root)

# Le bouton CSV est automatiquement disponible
root.mainloop()
```

### Exemple 2: Script autonome pour tester

```python
#!/usr/bin/env python3
from app.utils import read_csv_appareils, confirm_csv_import

# Lire le CSV
appareils, errors = read_csv_appareils("exemple_appareils.csv")

# Afficher les résultats
print(f"\n✓ {len(appareils)} appareil(s) chargé(s)")

if errors:
    print(f"\n⚠️ {len(errors)} erreur(s):")
    for error in errors:
        print(f"  - {error}")

# Afficher les appareils chargés
print("\nAppareils importés:")
for app in appareils:
    print(f"  • {app.libelle}: {app.puissance}W "
          f"({app.debut.strftime('%H:%M')}-{app.fin.strftime('%H:%M')}) "
          f"Tranche {app.tranche}")
```

## Flux utilisateur

```
1. Utilisateur clique "📥 Importer CSV"
                  ↓
2. Boîte de sélection de fichier
        (utilisateur choisit .csv)
                  ↓
3. Validation du CSV
   - Vérification colonnes
   - Parse des données
   - Détection erreurs
                  ↓
4. Fenêtre de confirmation
   - Aperçu des 10 premiers
   - Nombre total
   - Avertissements si erreurs
                  ↓
5. Utilisateur confirme?
        Oui → Import successful
         |    Appareils ajoutés 
         |    à la liste
         |
        Non → Annulation
```

## Points importants

✅ **Validation robuste** - Erreurs détaillées par ligne  
✅ **Non-bloquant** - Continue même s'il y a des erreurs  
✅ **Confirmation** - L'utilisateur voit ce qui arrive  
✅ **Formats flexibles** - Accepte plusieurs formats de temps  
✅ **Gestion UI** - Intégré tkinter  

## Fichier exemple

Utilisez `exemple_appareils.csv` pour tester avec des données réalistes.

## Prochaines amélirations possibles

- [ ] Export appareils vers CSV
- [ ] Validation des tranches contre la BD
- [ ] Affechage live du nombre de lecteurs/erreurs
- [ ] Option pour ignorer les erreurs et continuer
- [ ] Import depuis URL/API
- [ ] Détection automatique des formats de date
