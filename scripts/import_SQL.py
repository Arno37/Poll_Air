from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()  # Charge les variables du fichier .env

# Paramètres de connexion (à adapter)
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
host = os.getenv("PG_HOST", "localhost")
port = os.getenv("PG_PORT", 5432)
database = os.getenv("PG_DATABASE")

# Chaîne de connexion SQLAlchemy
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

# Colonnes à supprimer
colonnes_a_supprimer = [
    "date_maj", "code_zone", "coul_qual", "date_ech",
    "epsg_reg", "x_reg", "x_wgs84", "y_reg", "y_wgs84", "gml_id2"
]

# Dossier contenant les CSV
dossier = "../data/file-indices_qualite_air-01-01-2024_01-01-2025"
dossier_sortie = "../data/file-indices_nettoyes"
os.makedirs(dossier_sortie, exist_ok=True)

# Pour chaque fichier CSV du dossier
for fichier in os.listdir(dossier):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier, fichier)
        print(f"Nettoyage de {chemin} ...")
        # Lecture du CSV
        df = pd.read_csv(chemin)
        # Suppression des colonnes
        df = df.drop(columns=[col for col in colonnes_a_supprimer if col in df.columns])
        chemin_sortie = os.path.join(dossier_sortie, fichier)
        df.to_csv(chemin_sortie, index=False)
        print(f"Fichier nettoyé sauvegardé : {chemin_sortie}")

print("Tous les fichiers nettoyés sont dans le dossier file-indices_nettoyes.")