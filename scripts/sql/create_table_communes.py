from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_communes_simple():
    """Créer la table communes - Version ultra-simple"""
    
    print("🏗️ CRÉATION SIMPLE DE LA TABLE COMMUNES")
    print("=" * 42)
    
    with engine.connect() as conn:
        try:
            # 1. Supprimer et créer la table communes
            print("🏘️ Création table 'communes'...")
            
            conn.execute(text("DROP TABLE IF EXISTS communes CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE communes (
                    code_insee VARCHAR(10) PRIMARY KEY,
                    nom_commune VARCHAR(255) NOT NULL,
                    aasqa_code VARCHAR(10) NOT NULL,
                    departement VARCHAR(3),
                    region VARCHAR(100),
                    FOREIGN KEY (aasqa_code) REFERENCES aasqa_regions(aasqa_code)
                )
            """))
            
            print("   ✅ Structure créée")
            
            # 2. Insérer 9 communes (3 par région)
            print("📊 Insertion des communes...")
            
            communes_data = [
                # Martinique (AASQA 2)
                ('97209', 'Fort-de-France', '2', '972', 'Martinique'),
                ('97218', 'Le Lamentin', '2', '972', 'Martinique'),
                ('97231', 'Le Robert', '2', '972', 'Martinique'),
                
                # Normandie (AASQA 27)
                ('14118', 'Caen', '27', '14', 'Normandie'),
                ('76540', 'Rouen', '27', '76', 'Normandie'),
                ('50129', 'Cherbourg-en-Cotentin', '27', '50', 'Normandie'),
                
                # Eure-et-Loir (AASQA 28)
                ('28085', 'Chartres', '28', '28', 'Centre-Val de Loire'),
                ('28134', 'Dreux', '28', '28', 'Centre-Val de Loire'),
                ('28229', 'Lucé', '28', '28', 'Centre-Val de Loire')
            ]
            
            for code, nom, aasqa, dept, region in communes_data:
                conn.execute(text("""
                    INSERT INTO communes (code_insee, nom_commune, aasqa_code, departement, region)
                    VALUES (:code, :nom, :aasqa, :dept, :region)
                """), {
                    "code": code, "nom": nom, "aasqa": aasqa, 
                    "dept": dept, "region": region
                })
            
            # 3. COMMIT IMMÉDIAT
            conn.commit()
            print(f"   ✅ COMMIT effectué")
            
            # 4. Vérification
            count = conn.execute(text("SELECT COUNT(*) FROM communes")).fetchone()[0]
            print(f"   📊 {count} communes créées")
            
            # Afficher les communes créées
            communes = conn.execute(text("""
                SELECT nom_commune, aasqa_code, region 
                FROM communes 
                ORDER BY aasqa_code, nom_commune
            """)).fetchall()
            
            print(f"\n📋 COMMUNES CRÉÉES:")
            current_aasqa = None
            for nom, aasqa, region in communes:
                if aasqa != current_aasqa:
                    print(f"\n   🗺️ AASQA {aasqa} ({region}):")
                    current_aasqa = aasqa
                print(f"      • {nom}")
            
            print(f"\n🎉 TABLE COMMUNES CRÉÉE AVEC SUCCÈS !")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    create_communes_simple()