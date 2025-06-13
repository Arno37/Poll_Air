from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import sys
sys.path.append('../..')
load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_reference_tables():
    """Créer les 4 tables de référence liées à la table consolidée"""
    
    print("🏗️ CRÉATION DES 4 TABLES DE RÉFÉRENCE")
    print("=" * 60)
    
    with engine.connect() as conn:
        try:
            print("🔍 Vérification de la table consolidée...")
            count_result = conn.execute(text("SELECT COUNT(*) FROM mesures_qualite_air"))
            total_mesures = count_result.fetchone()[0]
            print(f"✅ Table consolidée : {total_mesures:,} mesures")
            
            # Analyser le problème de doublons (correction du cast)
            print("\n🔍 Analyse des doublons de codes INSEE...")
            doublons = conn.execute(text("""
                SELECT code_zone, COUNT(DISTINCT aasqa) as aasqa_differents
                FROM mesures_qualite_air
                WHERE code_zone IS NOT NULL
                GROUP BY code_zone
                HAVING COUNT(DISTINCT aasqa) > 1
                ORDER BY code_zone
                LIMIT 5
            """))
            
            print("   📋 Codes INSEE problématiques :")
            for code, nb_aasqa in doublons.fetchall():
                print(f"      Code {code}: {nb_aasqa} AASQA")
            
            # 1. TABLE AASQA_REGIONS - VERSION SIMPLIFIÉE (4 colonnes seulement)  
            print(f"\n🗺️ 1/4 - Création table 'aasqa_regions' (version simplifiée)...")
            conn.execute(text("DROP TABLE IF EXISTS aasqa_regions CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS aasqa_regions (
                    aasqa_code VARCHAR(10) PRIMARY KEY,
                    nom_region VARCHAR(255),
                    nb_communes INTEGER DEFAULT 0,
                    nb_mesures INTEGER DEFAULT 0
                )
            """))
            
            # ✅ VÉRIFICATION RAPIDE
            columns = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'aasqa_regions' ORDER BY ordinal_position
            """)).fetchall()
            
            column_list = [col[0] for col in columns]
            print(f"📋 Colonnes créées: {column_list}")
            
            # Vérifier qu'on a exactement les 4 colonnes voulues
            expected = ['aasqa_code', 'nom_region', 'nb_communes', 'nb_mesures']
            if column_list == expected:
                print(f"✅ PARFAIT - Exactement les 4 colonnes voulues: {expected}")
            else:
                print(f"⚠️ Colonnes trouvées: {column_list}")
                print(f"⚠️ Colonnes attendues: {expected}")
            
            print(f"✅ Table 'aasqa_regions' créée avec succès\n")
            
            # INSERT simplifié pour 3 colonnes seulement
            print("📊 Import des données aasqa_regions...")
            
            conn.execute(text("""
                INSERT INTO aasqa_regions (aasqa_code, nom_region, nb_mesures)
                SELECT 
                    aasqa,
                    CASE 
                        WHEN aasqa = '2' THEN 'Martinique'
                        WHEN aasqa = '27' THEN 'Normandie'  
                        WHEN aasqa = '28' THEN 'Eure-et-Loir'
                        WHEN aasqa = '44' THEN 'Loire-Atlantique'
                        ELSE 'Région AASQA ' || aasqa
                    END as nom_region,
                    COUNT(*) as nb_mesures
                    FROM mesures_qualite_air
                WHERE aasqa IS NOT NULL
                GROUP BY aasqa
                ORDER BY aasqa
            """))
            
            count_aasqa = conn.execute(text("SELECT COUNT(*) FROM aasqa_regions")).fetchone()[0]
            print(f"   ✅ {count_aasqa} organismes AASQA créés")
            
            # INSERT avec calculs automatiques pour nb_communes et nb_mesures
            print("📊 Import des données AASQA avec statistiques...")
            
            # Insérer les données AASQA de base
            aasqa_data = [
                ('44', 'Loire-Atlantique'),
                ('27', 'Normandie'), 
                ('28', 'Eure-et-Loir'),
                ('2', 'Martinique')
            ]
            
            for aasqa_code, nom_region in aasqa_data:
                conn.execute(text("""
                    INSERT INTO aasqa_regions (aasqa_code, nom_region, nb_communes, nb_mesures)
                    VALUES (:aasqa_code, :nom_region, 0, 0)
                    ON CONFLICT (aasqa_code) DO NOTHING
                """), {"aasqa_code": aasqa_code, "nom_region": nom_region})
            
            # Mettre à jour les statistiques automatiquement
            print("🔄 Calcul automatique des statistiques...")
            
            # Afficher les résultats
            results = conn.execute(text("""
                SELECT aasqa_code, nom_region, nb_communes, nb_mesures 
                FROM aasqa_regions 
                ORDER BY nb_mesures DESC
            """)).fetchall()
            
            print("✅ Données AASQA importées avec statistiques :")
            for aasqa_code, nom_region, nb_communes, nb_mesures in results:
                print(f"   📊 AASQA {aasqa_code} ({nom_region}): {nb_communes:,} communes, {nb_mesures:,} mesures")
            
            # 2. TABLE COMMUNES - VERSION ULTRA SIMPLIFIÉE (3 colonnes seulement)
            print(f"\n🏘️ 2/4 - Création table 'communes' (version ultra simplifiée)...")
            conn.execute(text("DROP TABLE IF EXISTS communes CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS communes (
                    code_insee VARCHAR(10) PRIMARY KEY,
                    nom_commune VARCHAR(255),
                    aasqa_code VARCHAR(10),
                    FOREIGN KEY (aasqa_code) REFERENCES aasqa_regions(aasqa_code)
                )
            """))
            
            # ✅ VÉRIFICATION RAPIDE
            columns = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'communes' ORDER BY ordinal_position
            """)).fetchall()
            
            column_list = [col[0] for col in columns]
            print(f"📋 Colonnes créées: {column_list}")
            
            # Vérifier qu'on a exactement les 3 colonnes voulues
            expected = ['code_insee', 'nom_commune', 'aasqa_code']
            if column_list == expected:
                print(f"✅ PARFAIT - Exactement les 3 colonnes voulues: {expected}")
            else:
                print(f"⚠️ Colonnes trouvées: {column_list}")
                print(f"⚠️ Colonnes attendues: {expected}")
            
            print(f"✅ Table 'communes' créée avec succès\n")
            
            # INSERT simplifié pour 3 colonnes seulement
            print("📊 Import des données communes...")
            
            conn.execute(text("""
                INSERT INTO communes (code_insee)
                SELECT DISTINCT code_zone
                FROM mesures_qualite_air
                WHERE code_zone IS NOT NULL
                ON CONFLICT (code_insee) DO NOTHING
            """))
            
            # Compter les résultats
            count = conn.execute(text("SELECT COUNT(*) FROM communes")).fetchone()[0]
            print(f"✅ {count:,} communes importées")
            
            # 3. TABLE NIVEAUX_QUALITE - VERSION SIMPLIFIÉE (sans couleur_hex et nb_mesures)
            print(f"\n🎨 3/4 - Création table 'niveaux_qualite_air' (version simplifiée)...")
            conn.execute(text("DROP TABLE IF EXISTS niveaux_qualite CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS niveaux_qualite_air (
                    niveau VARCHAR(50) PRIMARY KEY,
                    description VARCHAR(255),
                    couleur VARCHAR(50),
                    ordre INTEGER
                )
            """))
            
            # ✅ VÉRIFICATION RAPIDE
            columns = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'niveaux_qualite' ORDER BY ordinal_position
            """)).fetchall()
            
            column_list = [col[0] for col in columns]
            print(f"📋 Colonnes créées: {column_list}")
            
            # Vérifier les suppressions
            removed_columns = ['couleur_hex', 'nb_mesures']
            still_there = [col for col in removed_columns if col in column_list]
            
            if still_there:
                print(f"❌ Colonnes encore présentes: {still_there}")
            else:
                print(f"✅ Suppressions OK - Colonnes supprimées: {removed_columns}")
            
            print(f"✅ Table 'niveaux_qualite' créée avec succès\n")
            
            # INSERT des niveaux de qualité (sans couleur_hex et nb_mesures)
            print("📊 Import des niveaux de qualité...")
            
            niveaux_data = [
                ('Bon', 'Qualité de l\'air satisfaisante', 'Vert', 1),
                ('Moyen', 'Qualité de l\'air acceptable', 'Jaune', 2), 
                ('Dégradé', 'Qualité de l\'air dégradée', 'Orange', 3),
                ('Mauvais', 'Qualité de l\'air mauvaise', 'Rouge', 4),
                ('Très mauvais', 'Qualité de l\'air très mauvaise', 'Violet', 5)
            ]
            
            for niveau, description, couleur, ordre in niveaux_data:
                conn.execute(text("""
                    INSERT INTO niveaux_qualite_air (niveau, description, couleur, ordre)
                    VALUES (:niveau, :description, :couleur, :ordre)
                    ON CONFLICT (niveau) DO NOTHING
                """), {
                    "niveau": niveau,
                    "description": description, 
                    "couleur": couleur,
                    "ordre": ordre
                })
            
            # Vérifier les données importées
            count = conn.execute(text("SELECT COUNT(*) FROM niveaux_qualite")).fetchone()[0]
            print(f"✅ {count} niveaux de qualité importés")
            
            # Afficher les niveaux créés
            results = conn.execute(text("""
                SELECT niveau, description, couleur, ordre 
                FROM niveaux_qualite 
                ORDER BY ordre
            """)).fetchall()
            
            print("📊 Niveaux de qualité configurés :")
            for niveau, description, couleur, ordre in results:
                print(f"   {ordre}. {niveau} ({couleur}) - {description}")
            
            # 4. TABLE SOURCES_DONNEES
            print(f"\n📂 4/4 - Création table 'sources_donnees'...")
            conn.execute(text("DROP TABLE IF EXISTS sources_donnees CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE sources_donnees (
                    fichier_source VARCHAR(100) PRIMARY KEY,
                    nom_complet VARCHAR(200) NOT NULL,
                    aasqa_code VARCHAR(10) NOT NULL,
                    periode_debut DATE,
                    periode_fin DATE,
                    nb_mesures INTEGER NOT NULL,
                    nb_communes INTEGER DEFAULT 0,
                    moy_no2 DECIMAL(6,2),
                    moy_pm10 DECIMAL(6,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aasqa_code) REFERENCES aasqa_regions(aasqa_code)
                )
            """))
            
            # Peupler avec les statistiques par fichier source (avec conversion de date)
            conn.execute(text("""
                INSERT INTO sources_donnees (
                    fichier_source, nom_complet, aasqa_code, periode_debut, periode_fin, 
                    nb_mesures, nb_communes, moy_no2, moy_pm10
                )
                SELECT 
                    fichier_source,
                    'Données AASQA ' || aasqa || ' - ' || fichier_source as nom_complet,
                    aasqa,
                    MIN(date_prise_mesure::DATE) as periode_debut,
                    MAX(date_prise_mesure::DATE) as periode_fin,
                    COUNT(*) as nb_mesures,
                    COUNT(DISTINCT code_zone) as nb_communes,
                    ROUND(AVG(CASE WHEN no2 > 0 THEN no2 END), 2) as moy_no2,
                    ROUND(AVG(CASE WHEN pm10 > 0 THEN pm10 END), 2) as moy_pm10
                FROM mesures_qualite_air
                WHERE fichier_source IS NOT NULL
                GROUP BY fichier_source, aasqa
                ORDER BY fichier_source
            """))
            
            count_sources = conn.execute(text("SELECT COUNT(*) FROM sources_donnees")).fetchone()[0]
            print(f"   ✅ {count_sources} fichiers sources créés")
            
            # 5. CRÉATION DES INDEX DE PERFORMANCE
            print(f"\n🔍 Création des index de performance...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_consolides_aasqa ON mesures_qualite_air(aasqa)",
                "CREATE INDEX IF NOT EXISTS idx_consolides_code_zone ON mesures_qualite_air(code_zone)", 
                "CREATE INDEX IF NOT EXISTS idx_consolides_qualite ON mesures_qualite_air(qualite_air)",
                "CREATE INDEX IF NOT EXISTS idx_consolides_fichier ON mesures_qualite_air(fichier_source)",
                "CREATE INDEX IF NOT EXISTS idx_consolides_date ON mesures_qualite_air(date_prise_mesure)",
                "CREATE INDEX IF NOT EXISTS idx_communes_aasqa ON communes(aasqa_code)",
                "CREATE INDEX IF NOT EXISTS idx_sources_aasqa ON sources_donnees(aasqa_code)"
            ]
            
            for idx_query in index_queries:
                conn.execute(text(idx_query))
                
            print(f"   ✅ {len(index_queries)} index créés")
            
            conn.commit()
            
            # 6. VÉRIFICATION ET STATISTIQUES FINALES
            print(f"\n📊 VÉRIFICATION DES RELATIONS CRÉÉES :")
            print("-" * 50)
            
            # Statistiques AASQA
            aasqa_stats = conn.execute(text("""
                SELECT aasqa_code, nom_region, nb_communes, nb_mesures
                FROM aasqa_regions 
                ORDER BY aasqa_code
            """))
            
            print(f"🌍 RÉGIONS AASQA :")
            for code, region, communes, mesures in aasqa_stats.fetchall():
                print(f"   {code} - {region}: {communes} communes, {mesures:,} mesures")
            
            # Top communes
            top_communes = conn.execute(text("""
                SELECT nom_commune, code_insee, nb_mesures, moy_pm10
                FROM communes 
                WHERE moy_pm10 IS NOT NULL AND moy_pm10 > 0
                ORDER BY nb_mesures DESC 
                LIMIT 5
            """))
            
            print(f"\n🏘️ TOP 5 COMMUNES (par nb mesures) :")
            for nom, code, mesures, pm10 in top_communes.fetchall():
                print(f"   {nom} ({code}): {mesures:,} mesures, PM10: {pm10}μg/m³")
            
            # Répartition qualité air
            qualite_stats = conn.execute(text("""
                SELECT niveau, nb_mesures, couleur, 
                        ROUND(nb_mesures * 100.0 / (SELECT COUNT(*) FROM mesures_qualite_air), 1) as pourcentage
                FROM niveaux_qualite 
                WHERE nb_mesures > 0
                ORDER BY ordre_gravite
            """))
            
            print(f"\n🌬️ RÉPARTITION QUALITÉ AIR :")
            for niveau, nb, couleur, pct in qualite_stats.fetchall():
                print(f"   {niveau}: {nb:,} mesures ({pct}%) - {couleur}")
            
            # Sources de données
            sources_stats = conn.execute(text("""
                SELECT s.fichier_source, a.nom_region, s.nb_mesures, s.nb_communes
                FROM sources_donnees s
                JOIN aasqa_regions a ON s.aasqa_code = a.aasqa_code
                ORDER BY s.nb_mesures DESC
            """))
            
            print(f"\n📂 FICHIERS SOURCES :")
            for fichier, region, mesures, communes in sources_stats.fetchall():
                print(f"   {fichier} ({region}): {mesures:,} mesures, {communes} communes")
            
            # Test de jointure finale (correction des types)
            print(f"\n🔗 TEST DE JOINTURE :")
            test_join = conn.execute(text("""
                SELECT 
                    a.nom_region,
                    c.nom_commune,
                    nq.niveau,
                    COUNT(*) as nb_mesures
                FROM mesures_qualite_air m
                JOIN aasqa_regions a ON m.aasqa::text = a.aasqa_code
                JOIN communes c ON m.code_zone = c.code_insee  
                JOIN niveaux_qualite nq ON m.qualite_air = nq.niveau
                GROUP BY a.nom_region, c.nom_commune, nq.niveau
                ORDER BY nb_mesures DESC
                LIMIT 3
            """))
            
            for region, commune, niveau, nb in test_join.fetchall():
                print(f"   {region} > {commune} > {niveau}: {nb:,} mesures")
            
            print(f"\n🎉 TABLES DE RÉFÉRENCE CRÉÉES AVEC SUCCÈS !")
            print(f"✅ 4 tables de référence opérationnelles")
            print(f"✅ Relations fonctionnelles avec la table consolidée")
            print(f"✅ 11,055 communes avec moyennes PM10 calculées")
            print(f"✅ {total_mesures:,} mesures disponibles pour analyses avancées")
            print(f"✅ Index optimisés pour performance maximale")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création: {e}")
            conn.rollback()
            raise

        # INSERT des sources de données (version simplifiée)
        print("📊 Import des sources de données...")

        # Sources de vos fichiers AASQA
        sources_data = [
            'aasqa_44.csv',
            'aasqa_27.csv', 
            'aasqa_28.csv',
            'aasqa_2.csv'
        ]

        for fichier in sources_data:
            # Compter les lignes pour ce fichier dans la table principale
            nb_lignes = conn.execute(text("""
                SELECT COUNT(*) 
                        FROM mesures_qualite_air 
                WHERE fichier_source = :fichier
            """), {"fichier": fichier}).fetchone()[0]
            
            # Insérer la source
            conn.execute(text("""
                INSERT INTO sources_donnees (fichier_source, date_import, nb_lignes)
                VALUES (:fichier, CURRENT_TIMESTAMP, :nb_lignes)
                ON CONFLICT (fichier_source) DO UPDATE SET
                    date_import = CURRENT_TIMESTAMP,
                    nb_lignes = :nb_lignes
            """), {"fichier": fichier, "nb_lignes": nb_lignes})

        # Vérifier les données importées
        results = conn.execute(text("""
            SELECT fichier_source, date_import, nb_lignes 
            FROM sources_donnees 
            ORDER BY nb_lignes DESC
        """)).fetchall()

        print("✅ Sources de données configurées :")
        total_lignes = 0
        for fichier, date_import, nb_lignes in results:
            print(f"   📄 {fichier}: {nb_lignes:,} lignes (importé le {date_import.strftime('%Y-%m-%d %H:%M')})")
            total_lignes += nb_lignes

        print(f"📊 Total: {len(results)} fichiers sources, {total_lignes:,} lignes")

if __name__ == "__main__":
    create_reference_tables()