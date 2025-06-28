from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv('../../.env')

user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
host = os.getenv("PG_HOST", "localhost")
port = os.getenv("PG_PORT", 5432)
database = os.getenv("PG_DATABASE")

print("Connexion utilisée :", user, password, host, port, database)

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

table = "assqa_regions"
colonnes_a_supprimer = [
    "nb_mesures", "nb_communes"
]

with engine.connect() as conn:
    for col in colonnes_a_supprimer:
        try:
            print(f"Suppression de la colonne {col}...")
            conn.execute(text(f'ALTER TABLE {table} DROP COLUMN IF EXISTS {col}'))
        except Exception as e:
            print(f"Erreur lors de la suppression de {col} : {e}")
    conn.commit()
    print("✅ Suppression terminée !")