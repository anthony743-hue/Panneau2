import csv
from datetime import datetime, time
from pathlib import Path
from tkinter import messagebox, filedialog
from sqlalchemy.orm import selectinload

from app.database import session_scope
from app.exceptions import DataAccessError, ModelePanneauLoadError
from app.entity.Appareil import Appareil
from app.models.ConfigurationPanel import ConfigurationPanneauByTranche
from app.models.ConfigurationPrix import ConfigurationPrixPanneau
from app.models.modelePanneau import ModelePanneau
from app.models.TrancheHeure import TrancheHeure
from app.models.ConfigurationHeurePoint import ConfigurationHeurePoint

def calculateEnergyNeeded(period_label, appareils, res=None, isCharge=False):
    if res is None:
        return 0

    max_power = 0
    if not isCharge:
        for instant in res.get(period_label, {}).values():
            max_power = max(max_power, getSum(instant=instant, arr=appareils))
    else:
        for instant in res.get(period_label, {}).values():
            max_power +=  getSum(instant=instant, arr=appareils)
    return max_power

def getResult(appareils, modele_id=None, jour=1, modeles_data=None):
    if modele_id is None:
        modele_id = [1]

    if not modele_id or any(model_id <= 0 for model_id in modele_id):
        raise ValueError("ID de modele invalide.")
    if not appareils:
        raise ValueError("Aucun appareil fourni.")

    results = []
    configPrix = ConfigurationPrixPanneau.getAll()
    configHP = ConfigurationHeurePoint.getAll()
   
    for model_id in modele_id:
        configPercent = {}
        

        if modeles_data is not None:
            payload = _find_modele_payload(model_id=model_id, modeles_data=modeles_data)
            if payload is None:
                raise ValueError(f"Modele introuvable pour l'identifiant {model_id}.")

            configPercent = _build_percent_config(payload)
            configPrixModele = configPrix.get(model_id)
            configHPModele = configHP.get(model_id)

        result = getOutput(appareils, configPercent=configPercent, configPrix=configPrixModele, jour=jour, configHeurePoint=configHPModele)
        result["modele_id"] = model_id
        results.append(result)

    return results


def getOutput(appareils, configPercent=None, configPrix=None, jour=1, configHeurePoint=None):
    if not appareils:
        raise ValueError("Aucun appareil fourni.")

    configPercent = configPercent or {}
    configPrix = configPrix or {}
    configHeurePoint = configHeurePoint or {}

    tranches = get_default_tranches()
    grouped_instants = arrangeByPeriode(appareils=appareils, tranchesHeure=tranches)

    pourcentage_jour = convertToPercent(configPercent.get("maraina", 40))
    pourcentage_soir = convertToPercent(configPercent.get("hariva", 50))

    pic_jour = calculateEnergyNeeded(1, appareils, res=grouped_instants)
    pic_soir = calculateEnergyNeeded(2, appareils, res=grouped_instants)
    print(f"Pic jour : {pic_jour} || pic soir : {pic_soir}")
    
    batterie_theorique = calculateEnergyNeeded(3, appareils, res=grouped_instants, isCharge=True)
    charge_batterie = batterie_theorique / ( 11 + 2 * pourcentage_soir )

    energie_jour_unusued = getEnergyNotWorking(res=grouped_instants, trancheH=tranches[0], appareils=appareils, max_energy=pic_jour)
    energie_soir_unusued = getEnergyNotWorking(res=grouped_instants, trancheH=tranches[1], appareils=appareils, max_energy=pic_soir)

    prix_ouvrable, prix_non_ouvrable, energy1 = _calculate_unused_energy_price(energy_not_working=energie_jour_unusued,configPrix=configPrix, configHp=configHeurePoint)
    prix2_ouvrable, prix2_non_ouvrable, energy2 = _calculate_unused_energy_price(energy_not_working=energie_soir_unusued,configPrix=configPrix, configHp=configHeurePoint)

    puissance_panneau_minimale = getPowerSolarPanel(
        charge_batterie=charge_batterie,
        pic_jour=pic_jour,
        pic_soir=pic_soir,
        pourcentage_puissance_soir=pourcentage_soir,
    )

    return {
        "puissance_panneau_minimale_reel" :  round(puissance_panneau_minimale, 2), 
        "puissance_panneau_minimale": round(puissance_panneau_minimale, 2) / pourcentage_jour,
        "charge_batterie" : charge_batterie,
        "batterie_pratique": batterie_theorique * (1 + 0.5),
        "batterie_theorique": round(batterie_theorique, 2),
        "prix_enerige_non_ouvrable" : prix_non_ouvrable + prix2_non_ouvrable,
        "prix_enerige_ouvrable" : prix_ouvrable + prix2_ouvrable,
        "total_energy_unused" : energy1 + energy2,
    }


def getPowerSolarPanel(charge_batterie, pic_jour, pic_soir, pourcentage_puissance_soir=0.5):
    return (1 / (1 + pourcentage_puissance_soir)) * (2 * charge_batterie + pic_jour +pic_soir)

def getEnergyNotWorking(res, trancheH, appareils, max_energy=0):
    heures = trancheH.get_heures()
    ret = {}
    for heure in heures:
        temp = res.get(trancheH.id, {}).get(heure, [])
        print(f"Appareils travaillont a heure {heure} : {temp} \n")
        energy = getSum(instant=temp, arr=appareils)
        print(f"Energie a heure : {heure} a pour energy : {energy} : {max_energy}")
        ret[heure] = max(0, max_energy - energy)
    return ret


def getSum(instant, arr):
    return sum(arr[i].puissance for i in instant)


def arrangeByPeriode(appareils, tranchesHeure, res=None):
    target = res if res is not None else {}
    target.clear()

    tranches = list(tranchesHeure)
    tranches_by_id = {}

    for tranche in tranches:
        if tranche.id is None:
            raise ValueError("Chaque tranche doit avoir un identifiant.")

        tranches_by_id[tranche.id] = tranche
        target[tranche.id] = {}
        for heure in tranche.get_heures():
            target[tranche.id][heure] = []
    
    for index, appareil in enumerate(appareils):
        # if appareil.tranche not in tranches_by_id:
        #     raise ValueError(f"Tranche inconnue pour l'appareil '{appareil.libelle}'.")
        temp = TrancheHeure("temp", appareil.debut, appareil.fin)
        for heure in temp.get_heures():
            target[appareil.tranche][heure].append(index)

    return target


def get_heures_tranche(tranche):
    return tranche.get_heures()


def convertToPercent(value: int) -> float:
    return value / 100.0


def _find_modele_payload(model_id, modeles_data):
    for payload in modeles_data:
        modele = payload.get("modele")
        if modele is not None and modele.matches_id(model_id):
            return payload
    return None


def _build_percent_config(payload):
    modele = payload.get("modele")
    if modele is None:
        return {}
    return modele.build_percent_config(
        tranches=get_default_tranches(),
        configurations=payload.get("configurations_ensoleillement", []),
    )

def _calculate_unused_energy_price(energy_not_working,configPrix,configHp=None):
    s1 = 0
    s2 = 0
    s3 = 0
    price_ouvrable = configPrix[0]
    price_non_ouvrable = configPrix[1] 
    percent_a = 0
    percent_b = 0
    for key,val in energy_not_working.items():
        heure = key
        price_a = price_ouvrable 
        price_b = price_non_ouvrable
        found = False
        
        for h in configHp:
            if h.contains_time(heure):
                percent_a , percent_b = h.pourcentage_load()
                found= True
                break
        if found:
            price_a *= ( 1 + percent_a)
            price_b *= ( 1 + percent_b)
        s1+= price_a * val
        s2+= price_b * val
        s3+= val
    return s1, s2, s3

def get_default_tranches():
    try:
        with session_scope() as session:
            tranches = (
                session.query(TrancheHeure)
                .order_by(TrancheHeure.id)
                .all()
            )
            if tranches:
                return tranches
            raise DataAccessError(
                "Aucune tranche horaire disponible dans la base de donnees."
            )
    except DataAccessError:
        raise
    except Exception as exc:
        raise DataAccessError(
            "Erreur lors de la recuperation des tranches depuis la base de donnees."
        ) from exc


def get_modele_panneau_payloads():
    try:
        with session_scope() as session:
            modeles = (
                session.query(ModelePanneau)
                .options(
                    selectinload(ModelePanneau.configurations_ensoleillement)
                    .selectinload(ConfigurationPanneauByTranche.tranche_heure),
                    selectinload(ModelePanneau.configurations_prix),
                )
                .order_by(ModelePanneau.id)
                .all()
            )
            payloads = [
                modele.to_payload()
                for modele in modeles
            ]
            session.expunge_all()
    except Exception as exc:
        raise ModelePanneauLoadError(
            "Erreur lors de la recuperation des modeles de panneau depuis la base."
        ) from exc

    return payloads


def parse_time_from_csv(time_str):
    """
    Parse une chaîne de temps depuis le CSV.
    Accepte les formats: HH:MM:SS, HH:MM, HH
    """
    time_str = time_str.strip()
    formats = ("%H:%M:%S", "%H:%M", "%H")
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            pass
    
    raise ValueError(f"Format heure invalide: '{time_str}'. Utilise HH:MM ou HH:MM:SS.")


def read_csv_appareils(file_path):
    """
    Lit un fichier CSV pour charger des appareils.
    
    Structure du CSV attendue:
    - libelle (str): Nom de l'appareil [OBLIGATOIRE]
    - puissance (float): Puissance en watts [OBLIGATOIRE, >= 0]
    - debut (str): Heure de début HH:MM:SS [OBLIGATOIRE]
    - fin (str): Heure de fin HH:MM:SS [OBLIGATOIRE]
    - tranche (int): ID de la tranche horaire [OBLIGATOIRE, >= -1]
    
    Retourne une liste d'appareils (Appareil objects)
    """
    appareils = []
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if reader.fieldnames is None:
                raise ValueError("Le fichier CSV est vide.")
            
            # Vérifier les colonnes obligatoires
            required_columns = {'libelle', 'puissance', 'debut', 'fin', 'tranche'}
            missing_columns = required_columns - set(reader.fieldnames)
            
            if missing_columns:
                raise ValueError(
                    f"Colonnes manquantes dans le CSV: {', '.join(missing_columns)}\n"
                    f"Colonnes trouvées: {', '.join(reader.fieldnames)}"
                )
            
            for row_num, row in enumerate(reader, start=2):  # start=2 car ligne 1 est header
                try:
                    # Extraction et validation des champs
                    libelle = row['libelle'].strip()
                    if not libelle:
                        raise ValueError("Le libellé ne peut pas être vide")
                    
                    try:
                        puissance = float(row['puissance'].strip())
                    except ValueError:
                        raise ValueError(f"Puissance invalide: '{row['puissance']}', doit être un nombre")
                    
                    if puissance < 0:
                        raise ValueError(f"Puissance négative: {puissance}")
                    
                    debut = parse_time_from_csv(row['debut'])
                    fin = parse_time_from_csv(row['fin'])
                    
                    try:
                        tranche = int(row['tranche'].strip())
                    except ValueError:
                        raise ValueError(f"Tranche invalide: '{row['tranche']}', doit être un entier")
                    
                    # Créer l'objet Appareil
                    appareil = Appareil(
                        libelle=libelle,
                        puissance=puissance,
                        debut=debut,
                        fin=fin,
                        tranche=tranche
                    )
                    appareils.append(appareil)
                    
                except ValueError as e:
                    errors.append(f"Ligne {row_num}: {str(e)}")
                except Exception as e:
                    errors.append(f"Ligne {row_num}: Erreur inattendue - {str(e)}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier CSV n'existe pas: {file_path}")
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du CSV: {str(e)}")
    
    return appareils, errors


def confirm_csv_import(appareils, errors=None):
    """
    Affiche une fenêtre de confirmation pour l'import d'appareils depuis CSV.
    Retourne True si l'utilisateur confirme, False sinon.
    """
    errors = errors or []
    
    # Construire le message de confirmation
    message_parts = []
    
    if errors:
        message_parts.append("⚠️ AVERTISSEMENTS:")
        for error in errors:
            message_parts.append(f"  • {error}")
        message_parts.append("")
    
    message_parts.append(f"✓ {len(appareils)} appareil(s) seront importé(s):")
    message_parts.append("")
    
    # Afficher un aperçu des appareils
    for i, app in enumerate(appareils[:10], 1):  # Limite à 10 pour lisibilité
        message_parts.append(
            f"{i}. {app.libelle}: {app.puissance}W "
            f"({app.debut.strftime('%H:%M')} - {app.fin.strftime('%H:%M')}) "
            f"Tranche: {app.tranche}"
        )
    
    if len(appareils) > 10:
        message_parts.append(f"... et {len(appareils) - 10} autre(s)")
    
    message_parts.append("")
    message_parts.append("Êtes-vous sûr de vouloir importer ces appareils?")
    
    message = "\n".join(message_parts)
    
    # Afficher la boîte de dialogue de confirmation
    result = messagebox.askyesno(
        title="Confirmation d'import CSV",
        message=message
    )
    
    return result


def import_appareils_from_csv(parent_window):
    """
    Interface complète pour importer des appareils depuis un fichier CSV.
    Demande le chemin du fichier, valide, affiche une prévisualisation et confirm.
    
    Retourne les appareils créés ou None si annulé.
    """
    # Ouvrir la boîte de dialogue de sélection de fichier
    file_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Sélectionner un fichier CSV d'appareils",
        filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
    )
    
    if not file_path:  # L'utilisateur a annulé
        return None
    
    try:
        # Lire le CSV
        appareils, errors = read_csv_appareils(file_path)
        
        if not appareils and not errors:
            messagebox.showwarning(
                title="Fichier vide",
                message=f"Aucun appareil trouvé dans le fichier: {Path(file_path).name}"
            )
            return None
        
        # Demander la confirmation
        if confirm_csv_import(appareils, errors):
            messagebox.showinfo(
                title="Import réussi",
                message=f"✓ {len(appareils)} appareil(s) importé(s) avec succès!"
            )
            return appareils
        
        return None
        
    except FileNotFoundError as e:
        messagebox.showerror(
            title="Erreur fichier",
            message=f"Le fichier n'existe pas:\n{str(e)}"
        )
    except ValueError as e:
        messagebox.showerror(
            title="Erreur données CSV",
            message=f"Erreur dans le format du CSV:\n{str(e)}"
        )
    except Exception as e:
        messagebox.showerror(
            title="Erreur import",
            message=f"Une erreur s'est produite:\n{str(e)}"
        )
    
    return None
