#!/usr/bin/env python3
"""
SCRIPT D'INITIALISATION COMPLÈTE DE LA BASE DE DONNÉES POLLUTION
================================================================

Ce script permet de :
1. Créer toutes les tables nécessaires
2. Importer les données depuis les CSV
3. Appliquer la correction d'alignement
4. Créer les index et contraintes
5. Vérifier la qualité des données

Usage: python initialisation_complete.py
"""

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd
import time
from datetime import datetime

# Chargement de la configuration
load_dotenv('../../.env')

class DatabaseInitializer:
    def __init__(self):
        self.user = os.getenv("PG_USER")
        self.password = os.getenv("PG_PASSWORD")
        self.host = os.getenv("PG_HOST", "localhost")
        self.port = os.getenv("PG_PORT", 5432)
        self.database = os.getenv("PG_DATABASE")
        
        self.engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}")
        self.csv_folder = "../../data/file-indices_nettoyes"
        
    def log(self, message):
        """Affichage avec timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_connection(self):
        """Test de connexion à la base"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self.log(f"✅ Connexion PostgreSQL réussie")
                self.log(f"   Version: {version}")
                return True
        except Exception as e:
            self.log(f"❌ Erreur de connexion: {e}")
            return False
    
    def drop_existing_tables(self):
        """Suppression des tables existantes"""
        self.log("🗑️ Suppression des tables existantes...")
        
        tables = [
            'indices_qualite_air_consolides',
            'indices_qualite_assqa_2',
            'indices_qualite_assqa_27', 
            'indices_qualite_assqa_28',
            'indices_qualite_assqa_44'
        ]
        
        with self.engine.connect() as conn:
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
            self.log(f"   ✅ {len(tables)} tables supprimées")
    
    def import_csv_files(self):
        """Import des fichiers CSV dans des tables individuelles"""
        self.log("📥 Import des fichiers CSV...")
        
        csv_files = {
            'assqa_2.csv': 'indices_qualite_assqa_2',
            'assqa_27.csv': 'indices_qualite_assqa_27',
            'assqa_28.csv': 'indices_qualite_assqa_28',
            'assqa_44.csv': 'indices_qualite_assqa_44'
        }
        
        total_imported = 0
        
        for csv_file, table_name in csv_files.items():
            csv_path = os.path.join(self.csv_folder, csv_file)
            
            if not os.path.exists(csv_path):
                self.log(f"   ⚠️ Fichier introuvable: {csv_path}")
                continue
                
            self.log(f"   📄 Import de {csv_file}...")
            
            # Lecture du CSV
            df = pd.read_csv(csv_path, sep=';')
            
            # Import vers PostgreSQL
            df.to_sql(table_name, self.engine, if_exists='replace', index=True, index_label='id')
            
            count = len(df)
            total_imported += count
            self.log(f"      ✅ {count:,} lignes importées dans {table_name}")
        
        self.log(f"   📊 Total importé: {total_imported:,} lignes")
        return total_imported
    
    def create_consolidated_table(self):
        """Création de la table consolidée avec alignement correct"""
        self.log("🏗️ Création de la table consolidée...")
        
        with self.engine.connect() as conn:
            create_sql = """
                CREATE TABLE indices_qualite_air_consolides AS
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY t.table_order, t.original_id) as id,
                    t.aasqa, t.no2, t.o3, t.pm10, t.pm25,
                    t.date_correcte as date_prise_mesure,
                    t.qualite_correcte as qualite_air,
                    t.zone_correcte as zone,
                    t.source_correcte as source,
                    t.type_zone_correct as type_zone,
                    t.code_zone_correct as code_zone,
                    t.fichier_source
                FROM (
                    SELECT 1 as table_order, id as original_id, aasqa, no2, o3, pm10, pm25,
                           qualite_air as date_correcte,
                           libelle_zone as qualite_correcte,
                           source as zone_correcte,
                           type_zone as source_correcte,
                           'Région' as type_zone_correct,
                           CASE WHEN date_prise_mesure::text ~ '^[0-9]{5}$' 
                                THEN date_prise_mesure::text ELSE NULL END as code_zone_correct,
                           'assqa_2.csv' as fichier_source
                    FROM indices_qualite_assqa_2
                    
                    UNION ALL
                    
                    SELECT 2, id, aasqa, no2, o3, pm10, pm25,
                           qualite_air, libelle_zone, source, type_zone, 'Région',
                           CASE WHEN date_prise_mesure::text ~ '^[0-9]{5}$' 
                                THEN date_prise_mesure::text ELSE NULL END,
                           'assqa_27.csv'
                    FROM indices_qualite_assqa_27
                    
                    UNION ALL
                    
                    SELECT 3, id, aasqa, no2, o3, pm10, pm25,
                           qualite_air, libelle_zone, source, type_zone, 'Région',
                           CASE WHEN date_prise_mesure::text ~ '^[0-9]{5}$' 
                                THEN date_prise_mesure::text ELSE NULL END,
                           'assqa_28.csv'
                    FROM indices_qualite_assqa_28
                    
                    UNION ALL
                    
                    SELECT 4, id, aasqa, no2, o3, pm10, pm25,
                           qualite_air, libelle_zone, source, type_zone, 'Région',
                           CASE WHEN date_prise_mesure::text ~ '^[0-9]{5}$' 
                                THEN date_prise_mesure::text ELSE NULL END,
                           'assqa_44.csv'
                    FROM indices_qualite_assqa_44
                ) t
            """
            
            start_time = time.time()
            conn.execute(text(create_sql))
            creation_time = time.time() - start_time
            
            count = conn.execute(text("SELECT COUNT(*) FROM indices_qualite_air_consolides")).fetchone()[0]
            
            self.log(f"   ✅ Table consolidée créée en {creation_time:.1f}s avec {count:,} lignes")
            
            return count
    
    def create_constraints_and_indexes(self):
        """Création des contraintes et index"""
        self.log("🔑 Création des contraintes et index...")
        
        with self.engine.connect() as conn:
            # Clé primaire
            conn.execute(text("ALTER TABLE indices_qualite_air_consolides ADD PRIMARY KEY (id)"))
            
            # Index
            indexes = [
                'aasqa', 'code_zone', 'fichier_source', 
                'date_prise_mesure', 'qualite_air', 'zone'
            ]
            
            for col in indexes:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_consolides_{col} ON indices_qualite_air_consolides({col})"))
            
            conn.commit()
            self.log(f"   ✅ Clé primaire et {len(indexes)} index créés")
    
    def verify_data_quality(self):
        """Vérification de la qualité des données"""
        self.log("🔍 Vérification de la qualité des données...")
        
        with self.engine.connect() as conn:
            # Test global
            stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN date_prise_mesure ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2}$' THEN 1 END) as dates_ok,
                    COUNT(CASE WHEN code_zone ~ '^[0-9]{5}$' THEN 1 END) as codes_ok,
                    COUNT(CASE WHEN qualite_air IS NOT NULL THEN 1 END) as qualites_ok
                FROM indices_qualite_air_consolides
            """)).fetchone()
            
            total, dates_ok, codes_ok, qualites_ok = stats
            
            self.log(f"   📊 Statistiques globales:")
            self.log(f"      Total: {total:,} lignes")
            self.log(f"      Dates valides: {dates_ok:,} ({dates_ok/total*100:.1f}%)")
            self.log(f"      Codes INSEE: {codes_ok:,} ({codes_ok/total*100:.1f}%)")
            self.log(f"      Qualités renseignées: {qualites_ok:,} ({qualites_ok/total*100:.1f}%)")
            
            # Par fichier source
            by_source = conn.execute(text("""
                SELECT fichier_source, COUNT(*),
                       COUNT(CASE WHEN date_prise_mesure ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2}$' THEN 1 END) as dates_ok
                FROM indices_qualite_air_consolides
                GROUP BY fichier_source
                ORDER BY fichier_source
            """)).fetchall()
            
            self.log(f"   📁 Par fichier source:")
            for source, nb, dates_ok_file in by_source:
                pct = (dates_ok_file / nb * 100) if nb > 0 else 0
                self.log(f"      {source}: {nb:,} lignes | Dates OK: {pct:.1f}%")
            
            return dates_ok / total if total > 0 else 0
    
    def run_full_initialization(self):
        """Exécution complète de l'initialisation"""
        self.log("🚀 INITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Tests préliminaires
        if not self.test_connection():
            return False
        
        try:
            # 1. Nettoyage
            self.drop_existing_tables()
            
            # 2. Import CSV
            total_imported = self.import_csv_files()
            if total_imported == 0:
                self.log("❌ Aucune donnée importée")
                return False
            
            # 3. Consolidation
            consolidated_count = self.create_consolidated_table()
            
            # 4. Contraintes et index
            self.create_constraints_and_indexes()
            
            # 5. Vérification
            quality_score = self.verify_data_quality()
            
            # Résumé final
            total_time = time.time() - start_time
            
            self.log("=" * 60)
            if quality_score > 0.8:
                self.log("🎉 INITIALISATION RÉUSSIE !")
                self.log(f"✅ {consolidated_count:,} lignes consolidées")
                self.log(f"✅ {quality_score*100:.1f}% de données de qualité")
                self.log(f"✅ Temps total: {total_time:.1f} secondes")
                self.log("✅ Base de données prête pour l'API")
                return True
            else:
                self.log("⚠️ INITIALISATION PARTIELLE")
                self.log(f"⚠️ Qualité des données: {quality_score*100:.1f}%")
                return False
                
        except Exception as e:
            self.log(f"❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    initializer = DatabaseInitializer()
    success = initializer.run_full_initialization()
    
    if success:
        print("\n🏁 Votre base de données est opérationnelle !")
    else:
        print("\n❌ L'initialisation a échoué")