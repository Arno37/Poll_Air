import os
import pandas as pd

dossier_source = "../data/file-indices_qualite_air-01-06-2024_01-06-2025"
dossier_sortie = "../data/file-indices_nettoyes"
os.makedirs(dossier_sortie, exist_ok=True)

colonnes_a_supprimer = [
    "date_maj", "coul_qual", "date_ech",
    "epsg_reg", "x_reg", "x_wgs84", "y_reg", "y_wgs84", "gml_id2"
]

nouveaux_noms = [
    "aasqa", "no2", "o3", "pm10", "pm25", "code_zone",
    "date_prise_mesure", "qualite_air", "libelle_zone", "source", "type_zone"
]

for fichier in os.listdir(dossier_source):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier_source, fichier)
        print(f"Nettoyage de {chemin} ...")
        df = pd.read_csv(chemin)
        
        # Supprimer les colonnes indésirables
        colonnes_presentes = [col for col in colonnes_a_supprimer if col in df.columns]
        df = df.drop(columns=colonnes_presentes)
        print(f"Colonnes supprimées : {colonnes_presentes}")
        
        # Supprimer la 6e colonne (index 5) si elle existe encore
        if len(df.columns) > 6:
            colonne_supprimee = df.columns[6]
            df = df.drop(df.columns[6], axis=1)
            print(f"7e colonne '{colonne_supprimee}' supprimée pour : {fichier}")
        
        # Renommer les colonnes (si le nombre correspond)
        if len(df.columns) == len(nouveaux_noms):
            df.columns = nouveaux_noms
            print(f"✅ Colonnes renommées pour : {fichier}")
        else:
            print(f"⚠️ Nombre de colonnes inattendu dans {fichier} : {len(df.columns)}")
            continue
        
        # Ajoute la colonne fichier_source
        df["fichier_source"] = fichier
        
        # Mettre 'source' en première colonne
        colonnes = list(df.columns)
        colonnes.remove("source")
        colonnes = ["source"] + colonnes
        df = df[colonnes]
        
        chemin_sortie = os.path.join(dossier_sortie, fichier)
        df.to_csv(chemin_sortie, index=False)
        print(f"Fichier sauvegardé : {chemin_sortie}\n")

print("Tous les fichiers nettoyés sont dans le dossier file-indices_nettoyes.")