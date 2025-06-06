import os
import pandas as pd

dossier = "../data/file-indices_nettoyes"

nouveaux_noms = [
    "aasqa",        # 1ère colonne
    "NO2",          # 2e colonne
    "O3",           # 3e colonne
    "PM10",         # 4e colonne
    "PM25",         # 5e colonne
    # 6e colonne supprimée
    "date_prise_mesure",  # 7e colonne
    "qualite_air",        # 8e colonne
    "zone",               # 9e colonne
    "source",             # 10e colonne
    "type_zone"           # 11e colonne
]

for fichier in os.listdir(dossier):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier, fichier)
        df = pd.read_csv(chemin)
        # Supprimer la 6e colonne (index 5)
        df = df.drop(df.columns[5], axis=1)
        # Renommer les colonnes
        df.columns = nouveaux_noms
        df.to_csv(chemin, index=False)
        print(f"Colonnes renommées et 6e colonne supprimée pour : {chemin}")

print("Traitement terminé pour tous les fichiers.") 