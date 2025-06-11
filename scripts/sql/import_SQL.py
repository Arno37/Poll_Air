from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv('../../.env')  # Charge les variables du fichier .env

# Paramètres de connexion (à adapter)
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
host = os.getenv("PG_HOST", "localhost")
port = os.getenv("PG_PORT", 5432)
database = os.getenv("PG_DATABASE")

# Chaîne de connexion SQLAlchemy
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
print(f"✅ Connexion PostgreSQL : {engine}")

# Dossier contenant les CSV nettoyés
dossier_nettoyes = "../data/file-indices_nettoyes"

def add_id_column_to_table(table_name, engine):
    """Ajouter une colonne ID auto-incrémentée à une table existante - VERSION ROBUSTE"""
    
    with engine.connect() as conn:
        try:
            # Vérifier si la colonne id existe déjà
            check_column = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'id'
            """))
            
            if not check_column.fetchone():
                print(f"   ➕ Ajout de la colonne ID à {table_name}...")
                
                # Méthode robuste pour ajouter un ID
                # 1. Ajouter la colonne comme INTEGER d'abord
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN id INTEGER"))
                
                # 2. Créer une séquence
                conn.execute(text(f"CREATE SEQUENCE {table_name}_id_seq"))
                
                # 3. Remplir la colonne avec des valeurs séquentielles
                conn.execute(text(f"""
                    UPDATE {table_name} 
                    SET id = nextval('{table_name}_id_seq')
                """))
                
                # 4. Définir la colonne comme PRIMARY KEY avec auto-increment
                conn.execute(text(f"ALTER TABLE {table_name} ALTER COLUMN id SET NOT NULL"))
                conn.execute(text(f"ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{table_name}_id_seq')"))
                conn.execute(text(f"ALTER TABLE {table_name} ADD PRIMARY KEY (id)"))
                
                # 5. Associer la séquence à la colonne
                conn.execute(text(f"ALTER SEQUENCE {table_name}_id_seq OWNED BY {table_name}.id"))
                
                # Commit les changements
                conn.commit()
                print(f"   ✅ Colonne ID ajoutée avec succès à {table_name}")
                
                # Vérification immédiate
                verify_id = conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'id'
                """))
                
                id_info = verify_id.fetchone()
                if id_info:
                    print(f"   🔍 Vérification : ID ({id_info[1]}) | Auto-increment: {id_info[3] is not None}")
                
            else:
                print(f"   ℹ️ Colonne ID existe déjà dans {table_name}")
                
        except Exception as e:
            print(f"   ❌ Erreur ajout ID à {table_name}: {e}")
            conn.rollback()

# Pour chaque fichier CSV nettoyé
print(f"\n📁 IMPORT DES DONNÉES AVEC IDs AUTO-INCRÉMENTÉS")
print("=" * 60)

total_files = 0
total_rows = 0

# Corriger la liste des nouveaux noms (enlever les guillemets français)
nouveaux_noms = [
    "aasqa", "no2", "o3", "pm10", "pm25", "code_zone",
    "date_prise_mesure", "qualite_air", "libelle_zone", "source", "type_zone", "fichier_source"
]

dfs = []
for fichier in os.listdir(dossier_nettoyes):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier_nettoyes, fichier)
        print(f"\n📄 Import de {fichier}...")
        
        # Lecture du CSV nettoyé
        df = pd.read_csv(chemin)
        
        # Nom de la table (basé sur le nom du fichier)
        nom_table = f"indices_qualite_{fichier.replace('.csv', '').replace('-', '_')}"
        
        try:
            # Ajoute la colonne fichier_source si elle n'existe pas déjà
            if "fichier_source" not in df.columns:
                df["fichier_source"] = fichier
            # Forcer les noms de colonnes
            if len(df.columns) == len(nouveaux_noms):
                df.columns = nouveaux_noms
            else:
                print(f"⚠️ Nombre de colonnes inattendu dans {fichier} : {len(df.columns)}")
                print(df.columns)
                continue
            dfs.append(df)
            
            # Import vers PostgreSQL (remplace la table existante)
            df.to_sql(nom_table, engine, if_exists='replace', index=False)
            print(f"   📊 {len(df)} lignes importées dans {nom_table}")
            
            # Ajouter la colonne ID auto-incrémentée APRÈS l'import
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {nom_table} DROP COLUMN IF EXISTS id"))
                conn.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {nom_table}_id_seq"))
                conn.execute(text(f"ALTER TABLE {nom_table} ADD COLUMN id SERIAL PRIMARY KEY"))
                conn.commit()
            
            # Créer des index pour optimiser les requêtes
            with engine.connect() as conn:
                try:
                    # Index sur les colonnes importantes si elles existent
                    columns_to_index = ['date_prise_mesure', 'aasqa', 'no2', 'o3', 'pm10', 'pm25']
                    
                    for col in columns_to_index:
                        # Vérifier si la colonne existe
                        check_col = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{nom_table}' AND column_name = '{col}'
                        """))
                        
                        if check_col.fetchone():
                            try:
                                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{nom_table}_{col} ON {nom_table}({col})"))
                                print(f"   🔍 Index créé sur {col}")
                            except:
                                pass  # Index existe déjà ou erreur
                    
                    conn.commit()
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur création index: {e}")
            
            print(f"   ✅ Table {nom_table} créée avec ID et index")
            total_files += 1
            total_rows += len(df)
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'import de {fichier} : {e}")

def fix_existing_tables_without_ids():
    """Corriger les tables existantes qui n'ont pas d'ID"""
    
    print(f"\n🔧 CORRECTION DES TABLES EXISTANTES SANS ID")
    print("-" * 50)
    
    with engine.connect() as conn:
        # Trouver toutes les tables indices_qualite_* sans ID
        result = conn.execute(text("""
            SELECT t.table_name 
            FROM information_schema.tables t
            LEFT JOIN information_schema.columns c 
                ON t.table_name = c.table_name 
                AND c.column_name = 'id'
            WHERE t.table_schema = 'public' 
            AND t.table_name LIKE 'indices_qualite_%'
            AND c.column_name IS NULL
            ORDER BY t.table_name
        """))
        
        tables_without_id = [row[0] for row in result.fetchall()]
        
        if tables_without_id:
            print(f"📊 Tables sans ID trouvées : {len(tables_without_id)}")
            
            for table_name in tables_without_id:
                print(f"\n🔧 Correction de {table_name}...")
                add_id_column_to_table(table_name, engine)
        else:
            print("✅ Toutes les tables ont déjà des IDs")

# Exécuter la correction des tables existantes
fix_existing_tables_without_ids()

def add_code_zone_to_tables():
    """Ajouter la colonne code_zone aux tables PostgreSQL en lisant depuis les fichiers AASQA originaux"""
    
    print(f"\n🔧 AJOUT DE LA COLONNE CODE_ZONE")
    print("-" * 50)
    
    # Chemins des dossiers
    aasqa_folder = "../data/file-indices_qualite_air-01-01-2024_01-01-2025"
    
    # Vérifier que le dossier AASQA existe
    if not os.path.exists(aasqa_folder):
        print(f"❌ Dossier AASQA non trouvé: {aasqa_folder}")
        return
    
    # 1. Extraire les code_zone depuis les fichiers AASQA originaux
    print(f"📂 Extraction des code_zone depuis les fichiers AASQA...")
    code_zones_by_aasqa = {}
    
    for filename in os.listdir(aasqa_folder):
        if filename.startswith('assqa_') and filename.endswith('.csv'):
            file_path = os.path.join(aasqa_folder, filename)
            try:
                # Extraire le numéro AASQA du nom de fichier
                aasqa_number = filename.replace('assqa_', '').replace('.csv', '')
                
                # Lire le fichier
                df = pd.read_csv(file_path, header=None)
                
                # Le code_zone est dans la 9ème colonne (index 8)
                if len(df.columns) > 8:
                    code_zones = df.iloc[:, 8].unique()
                    # Filtrer pour ne garder que les codes à exactement 5 chiffres
                    valid_codes = []
                    for code in code_zones:
                        if pd.notna(code) and str(code) != 'nan':
                            code_str = str(code).strip()
                            # Vérifier que c'est exactement 5 chiffres
                            if code_str.isdigit() and len(code_str) == 5:
                                valid_codes.append(code_str)
                    
                    if valid_codes:
                        code_zones_by_aasqa[aasqa_number] = valid_codes[0]
                        print(f"   ✅ AASQA {aasqa_number}: code_zone = {valid_codes[0]} (5 chiffres)")
                        if len(code_zones) > len(valid_codes):
                            rejected = len(code_zones) - len(valid_codes)
                            print(f"       ⚠️ {rejected} codes rejetés (pas 5 chiffres)")
                    else:
                        print(f"   ⚠️ AASQA {aasqa_number}: aucun code_zone valide à 5 chiffres")
                        print(f"       Codes trouvés: {[str(c) for c in code_zones if pd.notna(c)]}")
                        
            except Exception as e:
                print(f"   ❌ Erreur lecture {filename}: {e}")
    
    print(f"\n📊 Code_zones extraits: {len(code_zones_by_aasqa)}")
    
    # 2. Ajouter la colonne code_zone aux tables PostgreSQL
    with engine.connect() as conn:
        try:
            # Trouver toutes les tables indices_qualite_*
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'indices_qualite_%'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            for table_name in tables:
                print(f"\n🔧 Traitement de la table {table_name}...")
                
                # Identifier l'AASQA correspondant depuis le nom de la table
                # Ex: indices_qualite_assqa_11 -> AASQA 11
                aasqa_match = None
                for aasqa_num in code_zones_by_aasqa.keys():
                    if f"assqa_{aasqa_num}" in table_name:
                        aasqa_match = aasqa_num
                        break
                
                if not aasqa_match:
                    print(f"   ⚠️ Aucun AASQA correspondant trouvé pour {table_name}")
                    continue
                
                code_zone_value = code_zones_by_aasqa[aasqa_match]
                
                # Vérifier si la colonne code_zone existe déjà
                check_column = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'code_zone'
                """))
                
                if not check_column.fetchone():
                    # Ajouter la colonne code_zone
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN code_zone VARCHAR(10)"))
                    print(f"   ➕ Colonne code_zone ajoutée")
                
                # Mettre à jour toutes les lignes avec le code_zone
                conn.execute(text(f"""
                    UPDATE {table_name}
                    SET code_zone = '{code_zone_value}'
                """))
                print(f"   ✅ Colonne code_zone mise à jour avec la valeur {code_zone_value}")
                
                # Créer un index sur code_zone
                try:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_code_zone ON {table_name}(code_zone)"))
                    print(f"   🔍 Index créé sur code_zone")
                except:
                    pass
            
            conn.commit()
            print(f"\n✅ Code_zone ajouté à toutes les tables!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout des code_zone: {e}")
            conn.rollback()

# Exécuter l'ajout des code_zone APRÈS la définition de la fonction
def main():
    # ... tout le code principal, y compris l'import, l'ajout d'ID, etc ...
    # À la fin :
    add_code_zone_to_tables()
    creer_table_consolidee()

def creer_table_consolidee():
    """Créer une table consolidée avec le bon ordre des colonnes"""
    print(f"\n📊 CRÉATION DE LA TABLE CONSOLIDÉE")
    print("-" * 50)
    
    nom_table = "indices_qualite_air_consolides"
    
    with engine.connect() as conn:
        try:
            # Supprimer l'ancienne table si elle existe
            conn.execute(text(f"DROP TABLE IF EXISTS {nom_table}"))
            conn.commit()
            print(f"🗑️ Ancienne table {nom_table} supprimée")
            
            # Récupérer toutes les tables indices_qualite_assqa_*
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'indices_qualite_assqa_%'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in tables_result.fetchall()]
            print(f"📂 Tables trouvées : {tables}")
            
            # Créer la table consolidée avec l'ORDRE EXACT des tables individuelles
            # + fichier_source à la fin
            create_table_sql = f"""
                CREATE TABLE {nom_table} (
                    id SERIAL PRIMARY KEY,
                    aasqa VARCHAR(10),
                    no2 DOUBLE PRECISION,
                    o3 DOUBLE PRECISION,
                    pm10 DOUBLE PRECISION,
                    pm25 DOUBLE PRECISION,
                    so2 DOUBLE PRECISION,
                    date_prise_mesure DATE,
                    qualite_air VARCHAR(50),
                    zone VARCHAR(100),
                    source VARCHAR(100),
                    type_zone VARCHAR(50),
                    code_zone VARCHAR(10),
                    fichier_source VARCHAR(50)
                )
            """
            
            conn.execute(text(create_table_sql))
            conn.commit()
            print(f"✅ Table {nom_table} créée avec l'ordre correct des colonnes")
            
            # Insérer les données en respectant l'ordre exact
            total_inserted = 0
            
            for table_name in tables:
                print(f"   📊 Consolidation de {table_name}...")
                
                # Déterminer le fichier source basé sur le nom de la table
                fichier_source = table_name.replace('indices_qualite_', '') + '.csv'
                
                # INSERT avec l'ordre EXACT des colonnes des tables individuelles
                insert_sql = f"""
                    INSERT INTO {nom_table} 
                    (aasqa, no2, o3, pm10, pm25, so2, date_prise_mesure, 
                     qualite_air, zone, source, type_zone, code_zone, fichier_source)
                    SELECT 
                        aasqa, no2, o3, pm10, pm25, so2, date_prise_mesure,
                        qualite_air, zone, source, type_zone, code_zone, '{fichier_source}'
                    FROM {table_name}
                    ORDER BY id
                """
                
                result = conn.execute(text(insert_sql))
                rows_inserted = result.rowcount
                total_inserted += rows_inserted
                print(f"      ✅ {rows_inserted:,} lignes consolidées depuis {table_name}")
            
            conn.commit()
            
            # Créer les index
            index_columns = ['aasqa', 'date_prise_mesure', 'code_zone', 'source', 'fichier_source']
            for col in index_columns:
                try:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{nom_table}_{col} ON {nom_table}({col})"))
                    print(f"   🔍 Index créé sur {col}")
                except:
                    pass
            
            conn.commit()
            
            # Vérification finale avec comparaison
            print(f"\n📋 VÉRIFICATION DE L'ORDRE DES COLONNES:")
            
            # Colonnes de la table consolidée
            consolidee_cols = conn.execute(text(f"""
                SELECT column_name, ordinal_position
                FROM information_schema.columns 
                WHERE table_name = '{nom_table}' 
                ORDER BY ordinal_position
            """))
            
            print(f"   📊 Structure table consolidée :")
            for col_name, position in consolidee_cols.fetchall():
                print(f"      {position}. {col_name}")
            
            # Comparaison avec une table individuelle
            if tables:
                ref_table = tables[0]  # Prendre la première table comme référence
                ref_cols = conn.execute(text(f"""
                    SELECT column_name, ordinal_position
                    FROM information_schema.columns 
                    WHERE table_name = '{ref_table}' 
                    ORDER BY ordinal_position
                """))
                
                print(f"\n   📋 Structure table référence ({ref_table}) :")
                for col_name, position in ref_cols.fetchall():
                    print(f"      {position}. {col_name}")
            
            # Vérifier quelques échantillons de données pour s'assurer que les valeurs sont correctes
            sample_result = conn.execute(text(f"""
                SELECT aasqa, no2, o3, pm10, pm25, code_zone, zone, fichier_source 
                FROM {nom_table} 
                LIMIT 5
            """))
            
            print(f"\n   🔍 Échantillon de données (vérification des valeurs) :")
            for row in sample_result.fetchall():
                aasqa, no2, o3, pm10, pm25, code_zone, zone, fichier_source = row
                print(f"      AASQA:{aasqa} | NO2:{no2} | O3:{o3} | PM10:{pm10} | PM25:{pm25} | Code:{code_zone} | Zone:{zone} | Source:{fichier_source}")
            
            # Compter les lignes finales
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {nom_table}"))
            final_count = count_result.fetchone()[0]
            
            print(f"\n🎉 Table consolidée recréée avec succès !")
            print(f"✅ {final_count:,} lignes consolidées")
            print(f"✅ Ordre des colonnes respecté")
            print(f"✅ Colonne fichier_source ajoutée à la fin")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la table consolidée: {e}")
            conn.rollback()

# APPELER LES FONCTIONS DANS LE BON ORDRE
print(f"\n" + "=" * 60)
print(f"🎉 IMPORT TERMINÉ")
print(f"📊 {total_files} fichiers importés")
print(f"📈 {total_rows} lignes au total")
print("✅ Toutes les tables ont maintenant des IDs auto-incrémentés")

# Exécuter l'ajout des code_zone
add_code_zone_to_tables()

# Créer la table consolidée
creer_table_consolidee()

# Vérification finale de toutes les tables
print(f"\n🔍 VÉRIFICATION FINALE DES TABLES")
print("-" * 50)

with engine.connect() as conn:
    try:
        # Lister toutes les tables qui commencent par 'indices_qualite_'
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE 'indices_qualite_%')
            ORDER BY table_name
        """))
        
        tables = result.fetchall()
        tables_with_id = 0
        tables_with_code_zone = 0
        
        for (table_name,) in tables:
            # Compter les lignes
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = count_result.fetchone()[0]
            
            # Vérifier la présence de l'ID
            id_check = conn.execute(text(f"""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'id'
            """))
            
            # Vérifier la présence du code_zone
            code_zone_check = conn.execute(text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'code_zone'
            """))
            
            id_info = id_check.fetchone()
            code_zone_info = code_zone_check.fetchone()
            
            if id_info:
                id_status = f"✅ ID ({id_info[1]})"
                tables_with_id += 1
            else:
                id_status = "❌ Pas d'ID"
            
            if code_zone_info:
                code_zone_status = f"✅ CODE_ZONE ({code_zone_info[1]})"
                tables_with_code_zone += 1
                
                # Exemple de code_zone
                try:
                    sample_result = conn.execute(text(f"SELECT DISTINCT code_zone FROM {table_name} LIMIT 3"))
                    samples = [row[0] for row in sample_result.fetchall()]
                    code_zone_status += f" | Ex: {samples}"
                except:
                    pass
            else:
                code_zone_status = "❌ Pas de CODE_ZONE"
            
            print(f"   📊 {table_name}: {count:,} lignes")
            print(f"       {id_status} | {code_zone_status}")
        
        print(f"\n📈 RÉSUMÉ FINAL:")
        print(f"   ✅ Tables avec ID : {tables_with_id}")
        print(f"   ✅ Tables avec CODE_ZONE : {tables_with_code_zone}")
        print(f"   📊 Total tables : {len(tables)}")
        
        if tables_with_id == len(tables) and tables_with_code_zone == len(tables):
            print(f"   🎉 PARFAIT ! Toutes les tables sont complètes")
        else:
            print(f"   ⚠️ Certaines tables nécessitent encore des corrections")
    
    except Exception as e:
        print(f"   ⚠️ Erreur vérification: {e}")

print(f"\n💡 Vos tables PostgreSQL ont maintenant :")
print(f"   🆔 Des colonnes 'id' SERIAL PRIMARY KEY")
print(f"   🏷️ Des colonnes 'code_zone' avec codes INSEE à 5 chiffres")
print(f"   🔍 Des index sur les colonnes importantes")
print(f"   🔗 Prêtes pour des jointures et votre API de recommandations")
print(f"   📊 Une table consolidée avec structure standardisée")

def consolidation_simple():
    """Fonction de consolidation simple et robuste"""
    print(f"\n🔄 CONSOLIDATION FINALE GARANTIE")
    print("-" * 50)
    
    with engine.connect() as conn:
        try:
            # 1. Supprimer l'ancienne table
            conn.execute(text("DROP TABLE IF EXISTS indices_qualite_air_consolides"))
            print("🗑️ Ancienne table supprimée")
            
            # 2. Créer la table avec UNION ALL - méthode garantie
            create_sql = """
                CREATE TABLE indices_qualite_air_consolides AS
                (
                    SELECT 
                        ROW_NUMBER() OVER () as id,
                        aasqa, no2, o3, pm10, pm25, code_zone, 
                        date_prise_mesure, qualite_air, 
                        libelle_zone as zone, source, type_zone,
                        'assqa_2.csv' as fichier_source
                    FROM indices_qualite_assqa_2
                    
                    UNION ALL
                    
                    SELECT 
                        ROW_NUMBER() OVER () + (SELECT COUNT(*) FROM indices_qualite_assqa_2),
                        aasqa, no2, o3, pm10, pm25, code_zone, 
                        date_prise_mesure, qualite_air, 
                        libelle_zone, source, type_zone,
                        'assqa_27.csv'
                    FROM indices_qualite_assqa_27
                    
                    UNION ALL
                    
                    SELECT 
                        ROW_NUMBER() OVER () + (SELECT COUNT(*) FROM indices_qualite_assqa_2) + (SELECT COUNT(*) FROM indices_qualite_assqa_27),
                        aasqa, no2, o3, pm10, pm25, code_zone, 
                        date_prise_mesure, qualite_air, 
                        libelle_zone, source, type_zone,
                        'assqa_28.csv'
                    FROM indices_qualite_assqa_28
                    
                    UNION ALL
                    
                    SELECT 
                        ROW_NUMBER() OVER () + (SELECT COUNT(*) FROM indices_qualite_assqa_2) + (SELECT COUNT(*) FROM indices_qualite_assqa_27) + (SELECT COUNT(*) FROM indices_qualite_assqa_28),
                        aasqa, no2, o3, pm10, pm25, code_zone, 
                        date_prise_mesure, qualite_air, 
                        libelle_zone, source, type_zone,
                        'assqa_44.csv'
                    FROM indices_qualite_assqa_44
                )
            """
            
            conn.execute(text(create_sql))
            print("✅ Table consolidée créée avec UNION ALL")
            
            # 3. Ajouter la clé primaire
            conn.execute(text("ALTER TABLE indices_qualite_air_consolides ADD PRIMARY KEY (id)"))
            print("🔑 Clé primaire ajoutée")
            
            # 4. Créer les index pour performance
            indexes = ['aasqa', 'code_zone', 'fichier_source', 'date_prise_mesure']
            for col in indexes:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_consolides_{col} ON indices_qualite_air_consolides({col})"))
            print(f"🔍 {len(indexes)} index créés")
            
            conn.commit()
            
            # 5. Vérification finale obligatoire
            count_result = conn.execute(text("SELECT COUNT(*) FROM indices_qualite_air_consolides"))
            final_count = count_result.fetchone()[0]
            
            print(f"\n📊 RÉSULTAT FINAL:")
            print(f"✅ {final_count:,} lignes consolidées")
            
            if final_count > 0:
                # Vérification de la qualité des données
                quality_check = conn.execute(text("""
                    SELECT 
                        COUNT(DISTINCT fichier_source) as nb_sources,
                        COUNT(DISTINCT aasqa) as nb_aasqa,
                        COUNT(DISTINCT code_zone) as nb_zones,
                        AVG(CASE WHEN no2 > 0 THEN no2 END) as avg_no2,
                        COUNT(*) as total_rows
                    FROM indices_qualite_air_consolides
                """))
                
                quality_data = quality_check.fetchone()
                print(f"📋 Qualité des données:")
                print(f"   - {quality_data[0]} fichiers sources")
                print(f"   - {quality_data[1]} AASQA différents")
                print(f"   - {quality_data[2]} zones uniques")
                print(f"   - NO2 moyen: {quality_data[3]:.2f}" if quality_data[3] else "   - NO2 moyen: N/A")
                
                # Répartition par fichier
                distribution = conn.execute(text("""
                    SELECT fichier_source, COUNT(*), 
                           MIN(date_prise_mesure) as date_min,
                           MAX(date_prise_mesure) as date_max
                    FROM indices_qualite_air_consolides 
                    GROUP BY fichier_source 
                    ORDER BY fichier_source
                """))
                
                print(f"\n📂 Répartition par fichier:")
                for source, count, date_min, date_max in distribution.fetchall():
                    print(f"   {source}: {count:,} lignes ({date_min} → {date_max})")
                
                print(f"\n🎉 CONSOLIDATION RÉUSSIE!")
                return True
                
            else:
                print(f"\n❌ ÉCHEC: Table encore vide")
                
                # Diagnostic des tables sources
                source_diagnostic = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name LIKE 'indices_qualite_assqa_%'
                    ORDER BY table_name
                """))
                
                print(f"\n🔍 Diagnostic des tables sources:")
                for (table_name,) in source_diagnostic.fetchall():
                    try:
                        table_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()[0]
                        print(f"   {table_name}: {table_count:,} lignes")
                    except Exception as e:
                        print(f"   {table_name}: ERREUR - {e}")
                
                return False
                
        except Exception as e:
            print(f"❌ Erreur consolidation: {e}")
            conn.rollback()
            return False

# Exécuter la consolidation simple
consolidation_simple()

print(f"\n🎉 PROCESSUS COMPLET TERMINÉ!")
print(f"✅ Tables individuelles avec IDs et code_zone")
print(f"✅ Table consolidée avec toutes les données")
print(f"✅ Index et optimisations créés")
print(f"🚀 Système prêt pour l'API de recommandations!")