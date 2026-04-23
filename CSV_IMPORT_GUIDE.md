# Fonctionnalité Import CSV Appareils

## Description

Cette fonctionnalité permet d'importer batch d'appareils depuis un fichier CSV avec validation et confirmation préalable.

## Fonctions créées dans `app/utils.py`

### 1. `parse_time_from_csv(time_str)`
Parse une chaîne de temps avec les formats: `HH:MM:SS`, `HH:MM`, ou `HH`

```python
time_obj = parse_time_from_csv("14:30:00")  # → time(14, 30, 0)
time_obj = parse_time_from_csv("14:30")     # → time(14, 30, 0)
```

### 2. `read_csv_appareils(file_path)`
Lit et valide un fichier CSV, retourne une liste d'appareils et une liste d'erreurs.

```python
appareils, errors = read_csv_appareils("path/to/file.csv")

if errors:
    for error in errors:
        print(f"Erreur: {error}")
        
for app in appareils:
    print(f"{app.libelle}: {app.puissance}W")
```

### 3. `confirm_csv_import(appareils, errors=None)`
Affiche une fenêtre de confirmation avec aperçu des appareils à importer.

### 4. `import_appareils_from_csv(parent_window)` ⭐
Fonction complète qui orchestre le processus entier:
- Ouvre un sélecteur de fichier
- Valide le CSV
- Affiche une prévisualisation
- Demande confirmation
- Retourne les appareils ou `None` si annulé

## Format du fichier CSV

Le fichier CSV doit avoir les colonnes suivantes (ordre indifférent):

```
libelle,puissance,debut,fin,tranche
```

### Description des colonnes:

| Colonne | Type | Obligatoire | Description | Exemple |
|---------|------|-------------|-------------|---------|
| libelle | str | ✓ | Nom de l'appareil | "Réfrigérateur" |
| puissance | float | ✓ | Puissance en watts (≥ 0) | 500 |
| debut | str | ✓ | Heure de démarrage (HH:MM:SS) | "06:00:00" |
| fin | str | ✓ | Heure d'arrêt (HH:MM:SS) | "22:00:00" |
| tranche | int | ✓ | ID de tranche horaire (≥ -1) | 1 |

### Exemple de fichier CSV:

```csv
libelle,puissance,debut,fin,tranche
Réfrigérateur,500,06:00:00,22:00:00,1
Lave-linge,2000,08:00:00,09:00:00,1
Climatisation,3000,12:00:00,17:00:00,1
Ordinateur,200,09:00:00,18:00:00,1
Chauffe-eau,4000,06:00:00,07:00:00,1
Télévision,150,19:00:00,23:00:00,2
```

## Utilisation dans le contrôleur

### Exemple 1: Intégration simple
```python
from app.utils import import_appareils_from_csv

# Dans AppareilFormController
def import_from_csv_button_clicked(self):
    appareils = import_appareils_from_csv(self.root)
    
    if appareils:
        for appareil in appareils:
            self.appareils.append(appareil)
            self._insert_appareil_row(len(self.appareils) - 1, appareil)
```

### Exemple 2: Avec gestion des erreurs personnalisée
```python
from app.utils import read_csv_appareils, confirm_csv_import
from tkinter import filedialog, messagebox

def import_csv_manual(self):
    file_path = filedialog.askopenfilename(
        parent=self.root,
        title="Sélectionner CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not file_path:
        return
    
    try:
        appareils, errors = read_csv_appareils(file_path)
        
        if errors:
            messagebox.showwarning(
                "Avertissements",
                f"{len(errors)} erreur(s) lors de la lecture:\n" +
                "\n".join(errors[:5])
            )
        
        if appareils and confirm_csv_import(appareils, errors):
            self.appareils.extend(appareils)
            self._refresh_view()
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Import échoué: {str(e)}")
```

## Validation effectuée

✓ Vérification des colonnes obligatoires  
✓ Parse des heures avec formats multiples  
✓ Validation de la puissance (≥ 0)  
✓ Validation du libellé (non vide)  
✓ Validation des tranches (entier ≥ -1)  
✓ Gestion des erreurs par ligne  
✓ Confirmation avant import  

## Gestion des erreurs

- ❌ **Fichier introuvable**: Détecté et utilisateur informé
- ❌ **Format invalide**: Détail par ligne du problème
- ❌ **Colonnes manquantes**: Liste les colonnes requises
- ❌ **Données invalides**: Indique le type erreur et la valeur

Chaque erreur est cataloguée et affichée sans arrêter la lecture du reste du fichier.

## Tests

Un fichier `exemple_appareils.csv` est fourni pour tester la fonctionnalité.

```bash
# Test simple
python3
>>> from app.utils import read_csv_appareils
>>> appareils, errors = read_csv_appareils("exemple_appareils.csv")
>>> print(f"Chargé: {len(appareils)} appareils")
>>> print(f"Erreurs: {len(errors)}")
```

## Notes

- La fonction `import_appareils_from_csv()` nécessite `parent_window` (la fenêtre tkinter principal)
- Les formats de temps flexibles permettent "14:30:00", "14:30", ou "14"
- Les identifiants de tranches doivent exister dans la base ou être -1
- Le CSV est lu en UTF-8 (compatible accents français)
