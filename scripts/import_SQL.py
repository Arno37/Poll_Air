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
print(engine)

# Dossier contenant les CSV nettoyés
dossier_nettoyes = "../data/file-indices_nettoyes"

# Pour chaque fichier CSV nettoyé
for fichier in os.listdir(dossier_nettoyes):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier_nettoyes, fichier)
        print(f"Import de {chemin} vers PostgreSQL...")
        
        # Lecture du CSV nettoyé
        df = pd.read_csv(chemin)
        
        # Nom de la table (basé sur le nom du fichier)
        nom_table = f"indices_qualite_{fichier.replace('.csv', '').replace('-', '_')}"
        
        try:
            # Import vers PostgreSQL
            df.to_sql(nom_table, engine, if_exists='replace', index=False)
            print(f"✅ Données importées dans la table : {nom_table}")
        except Exception as e:
            print(f"❌ Erreur lors de l'import de {fichier} : {e}")

print("Import vers PostgreSQL terminé.")