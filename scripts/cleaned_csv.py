import os
import pandas as pd

dossier_source = "../data/file-indices_qualite_air-01-01-2024_01-01-2025"
dossier_sortie = "../data/file-indices_nettoyes"
os.makedirs(dossier_sortie, exist_ok=True)

colonnes_a_supprimer = [
    "date_maj", "code_zone", "coul_qual", "date_ech",
    "epsg_reg", "x_reg", "x_wgs84", "y_reg", "y_wgs84", "gml_id2"
]

for fichier in os.listdir(dossier_source):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier_source, fichier)
        print(f"Nettoyage de {chemin} ...")
        df = pd.read_csv(chemin)
        colonnes_presentes = [col for col in colonnes_a_supprimer if col in df.columns]
        df = df.drop(columns=colonnes_presentes)
        chemin_sortie = os.path.join(dossier_sortie, fichier)
        df.to_csv(chemin_sortie, index=False)
        print(f"Fichier nettoyé sauvegardé : {chemin_sortie}")

print("Tous les fichiers nettoyés sont dans le dossier file-indices_nettoyes.") 