"""
🚀 IMPORT SIMPLIFIÉ - Concaténation et import des 3 fichiers CSV AASQA
Assqa_2 (Martinique) + Assqa_27 (Normandie) + Assqa_28 (Eure-et-Loir)
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv('../../.env')  # Charge les variables du fichier .env

def import_csv_simple():
    print("🚀 IMPORT SIMPLIFIÉ - CONCATÉNATION 3 FICHIERS CSV")
    print("=" * 60)
    
    # 1. CONNEXION BASE DE DONNÉES
    print("🔌 Connexion à PostgreSQL...")
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASSWORD")
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", 5432)
    database = os.getenv("PG_DATABASE")
    
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    print(f"   ✅ Connexion OK: {host}:{port}/{database}")
    
    # 2. DÉFINIR LES FICHIERS À CONCATÉNER
    data_folder = "../../data/file-indices_qualite_air-01-06-2024_01-06-2025"
    fichiers_csv = ["assqa_2.csv", "assqa_27.csv", "assqa_28.csv"]
    
    print(f"\n📊 Fichiers à traiter:")
    for fichier in fichiers_csv:
        chemin = os.path.join(data_folder, fichier)
        if os.path.exists(chemin):
            taille = os.path.getsize(chemin) / (1024*1024)  # Taille en MB
            print(f"   ✅ {fichier} ({taille:.1f} MB)")
        else:
            print(f"   ❌ {fichier} INTROUVABLE")
            return False
    
    # 3. LECTURE ET CONCATÉNATION
    print(f"\n🔄 Lecture et concaténation des fichiers...")
    dataframes = []
    
    for fichier in fichiers_csv:
        chemin = os.path.join(data_folder, fichier)
        print(f"   📂 Lecture {fichier}...")
        
        try:
            df = pd.read_csv(chemin, encoding='utf-8')
            print(f"      📊 {len(df):,} lignes trouvées")
            dataframes.append(df)
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
            return False
    
    # Concaténation
    df_final = pd.concat(dataframes, ignore_index=True)
    print(f"\n✅ Concaténation terminée: {len(df_final):,} lignes totales")
    
    # 4. NETTOYAGE DE LA TABLE EXISTANTE
    print(f"\n🗑️ Nettoyage de la table existante...")
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS indices_qualite_air_consolides CASCADE"))
            conn.commit()
            print(f"   ✅ Table supprimée")
        except Exception as e:
            print(f"   ⚠️ Pas de table à supprimer: {e}")
    
    # 5. IMPORT DANS POSTGRESQL
    print(f"\n📥 Import dans PostgreSQL...")
    try:
        df_final.to_sql(
            'indices_qualite_air_consolides',
            engine,
            index=False,  # Pas d'index pandas
            if_exists='replace',  # Remplacer si existe
            method='multi',  # Import optimisé
            chunksize=1000  # Par chunks de 1000 lignes
        )
        print(f"   ✅ Import terminé: {len(df_final):,} lignes importées")
        
        # 6. AJOUTER UNE CLÉ PRIMAIRE
        print(f"\n🔑 Ajout d'une clé primaire...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE indices_qualite_air_consolides ADD COLUMN id SERIAL PRIMARY KEY"))
            conn.commit()
            print(f"   ✅ Clé primaire ajoutée")
        
        # 7. VÉRIFICATION FINALE
        print(f"\n✅ VÉRIFICATION FINALE:")
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM indices_qualite_air_consolides")).fetchone()[0]
            print(f"   📊 Lignes en base: {count:,}")
            
            # Échantillon
            sample = conn.execute(text("SELECT * FROM indices_qualite_air_consolides LIMIT 3")).fetchall()
            print(f"   📋 Échantillon:")
            for row in sample:
                print(f"      - AASQA: {row[0]} | Date: {row[6]} | Qualité: {row[7]}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    print("🎯 DÉMARRAGE IMPORT SIMPLIFIÉ")
    print("Fichiers: assqa_2.csv + assqa_27.csv + assqa_28.csv")
    print("-" * 60)
    
    try:
        succes = import_csv_simple()
        
        if succes:
            print(f"\n🎉 IMPORT TERMINÉ AVEC SUCCÈS !")
            print(f"📊 Table 'indices_qualite_air_consolides' prête")
        else:
            print(f"\n❌ ÉCHEC DE L'IMPORT")
            print(f"🔍 Vérifiez les fichiers CSV et la configuration PostgreSQL")
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()