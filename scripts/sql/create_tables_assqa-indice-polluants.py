from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import sys
sys.path.append('../..')
load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_architecture_tables():
    """Créer les 3 tables architecturales de base"""
    
    print("🏗️ CRÉATION DE L'ARCHITECTURE DE BASE")
    print("=" * 50)
    
    with engine.connect() as conn:
        try:
            # 1. TABLE AASQA_REGIONS
            print(f"\n🗺️ 1/3 - Création table 'aasqa_regions'...")
            conn.execute(text("DROP TABLE IF EXISTS aasqa_regions CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE aasqa_regions (
                    aasqa_code VARCHAR(10) PRIMARY KEY,
                    nom_region VARCHAR(255),
                    nb_communes INTEGER DEFAULT 0,
                    nb_mesures INTEGER DEFAULT 0
                )
            """))
            
            # INSERT des données AASQA
            aasqa_data = [
                ('2', 'Martinique'),
                ('27', 'Normandie'), 
                ('28', 'Eure-et-Loir'),
                ('44', 'Loire-Atlantique')
            ]
            
            for aasqa_code, nom_region in aasqa_data:
                conn.execute(text("""
                    INSERT INTO aasqa_regions (aasqa_code, nom_region)
                    VALUES (:aasqa_code, :nom_region)
                """), {"aasqa_code": aasqa_code, "nom_region": nom_region})
            
            count_aasqa = conn.execute(text("SELECT COUNT(*) FROM aasqa_regions")).fetchone()[0]
            print(f"   ✅ {count_aasqa} régions AASQA créées")
            
            # 2. TABLE INDICE (niveaux de qualité)
            print(f"\n🎨 2/3 - Création table 'indice'...")
            conn.execute(text("DROP TABLE IF EXISTS indice CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE indice (
                    niveau VARCHAR(50) PRIMARY KEY,
                    description VARCHAR(255),
                    couleur VARCHAR(50),
                    ordre INTEGER
                )
            """))
            
            # INSERT des niveaux de qualité
            niveaux_data = [
                ('Bon', 'Qualité de l\'air satisfaisante', 'Vert', 1),
                ('Moyen', 'Qualité de l\'air acceptable', 'Jaune', 2), 
                ('Dégradé', 'Qualité de l\'air dégradée', 'Orange', 3),
                ('Mauvais', 'Qualité de l\'air mauvaise', 'Rouge', 4),
                ('Très mauvais', 'Qualité de l\'air très mauvaise', 'Violet', 5)
            ]
            
            for niveau, description, couleur, ordre in niveaux_data:
                conn.execute(text("""
                    INSERT INTO indice (niveau, description, couleur, ordre)
                    VALUES (:niveau, :description, :couleur, :ordre)
                """), {
                    "niveau": niveau,
                    "description": description, 
                    "couleur": couleur,
                    "ordre": ordre
                })
            
            count_indice = conn.execute(text("SELECT COUNT(*) FROM indice")).fetchone()[0]
            print(f"   ✅ {count_indice} niveaux de qualité créés")
            
            # 3. TABLE POLLUANTS
            print(f"\n🧪 3/3 - Création table 'polluants'...")
            conn.execute(text("DROP TABLE IF EXISTS polluants CASCADE"))
            conn.execute(text("""
                CREATE TABLE polluants (
                    code_polluant VARCHAR(10) PRIMARY KEY,
                    nom_polluant VARCHAR(100),
                    unite_mesure VARCHAR(20)
                )
            """))
              # INSERT des polluants
            polluants_data = [
                ('NO2', 'Dioxyde d\'azote', 'µg/m³'),
                ('PM10', 'Particules fines PM10', 'µg/m³'),
                ('PM2.5', 'Particules fines PM2.5', 'µg/m³'),
                ('O3', 'Ozone', 'µg/m³'),
                ('SO2', 'Dioxyde de soufre', 'µg/m³')
            ]
            
            for code, nom, unite in polluants_data:
                conn.execute(text("""
                    INSERT INTO polluants (code_polluant, nom_polluant, unite_mesure)
                    VALUES (:code, :nom, :unite)
                """), {
                    "code": code, "nom": nom, "unite": unite
                })
            
            count_polluants = conn.execute(text("SELECT COUNT(*) FROM polluants")).fetchone()[0]
            print(f"   ✅ {count_polluants} polluants créés")
            
            # COMMIT
            conn.commit()
            
            # VÉRIFICATION FINALE
            print(f"\n🎉 ARCHITECTURE CRÉÉE AVEC SUCCÈS !")
            print("-" * 40)
            
            # Afficher les régions AASQA
            print("🗺️ RÉGIONS AASQA :")
            regions = conn.execute(text("SELECT aasqa_code, nom_region FROM aasqa_regions ORDER BY aasqa_code")).fetchall()
            for code, nom in regions:
                print(f"   {code}: {nom}")
            
            # Afficher les niveaux de qualité
            print("\n🎨 NIVEAUX DE QUALITÉ :")
            niveaux = conn.execute(text("SELECT niveau, couleur, ordre FROM indice ORDER BY ordre")).fetchall()
            for niveau, couleur, ordre in niveaux:
                print(f"   {ordre}. {niveau} ({couleur})")
            
            # Afficher les polluants
            print("\n🧪 POLLUANTS SURVEILLÉS :")
            polluants = conn.execute(text("SELECT code_polluant, nom_polluant, unite_mesure FROM polluants ORDER BY code_polluant")).fetchall()
            for code, nom, unite in polluants:
                print(f"   {code}: {nom} ({unite})")
            print(f"\n✅ 3 tables architecturales opérationnelles")
            print(f"✅ Prêt pour l'import des données principales")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    create_architecture_tables()