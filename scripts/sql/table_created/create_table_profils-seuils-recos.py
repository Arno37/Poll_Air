import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")


def create_profils_tables():
    """Crée les 3 tables nécessaires pour le système de recommandation"""
    
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST'),
        database=os.getenv('PG_NAME'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD')
    )
    cursor = conn.cursor()
    
    try:
        print("🏗️  Création des tables pour système de recommandation...")
        
        # TABLE 1 : profils_utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profils_utilisateurs (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE,
                type_profil VARCHAR(20) NOT NULL 
                    CHECK (type_profil IN ('sportif', 'sensible', 'parent', 'senior')),
                age_groupe VARCHAR(20) 
                    CHECK (age_groupe IN ('18-30', '30-50', '50-65', '65+')),
                pathologies TEXT[] DEFAULT '{}',
                activites_pratiquees TEXT[] DEFAULT '{}',
                commune_residence CHAR(5) REFERENCES communes(code_insee),
                niveau_sensibilite VARCHAR(10) DEFAULT 'moyen'
                    CHECK (niveau_sensibilite IN ('faible', 'moyen', 'eleve')),
                notifications_actives BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'profils_utilisateurs' créée")
        
        # TABLE 2 : seuils_personnalises
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seuils_personnalises (
                id SERIAL PRIMARY KEY,
                profil_type VARCHAR(20) NOT NULL
                    CHECK (profil_type IN ('sportif', 'sensible', 'parent', 'senior')),
                polluant VARCHAR(10) NOT NULL,
                seuil_info INTEGER NOT NULL,
                seuil_alerte INTEGER NOT NULL,
                pourcentage_reduction INTEGER DEFAULT 20,
                conseil_depassement TEXT,
                FOREIGN KEY (polluant) REFERENCES polluants(code_polluant),
                UNIQUE(profil_type, polluant)
            );
        """)
        print("✅ Table 'seuils_personnalises' créée")
        
        # TABLE 3 : recommandations_base
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommandations_base (
                id SERIAL PRIMARY KEY,
                profil_cible VARCHAR(20) NOT NULL
                    CHECK (profil_cible IN ('sportif', 'sensible', 'parent', 'senior')),
                niveau_pollution VARCHAR(20) NOT NULL
                    CHECK (niveau_pollution IN ('bon', 'moyen', 'degrade', 'mauvais', 'tres_mauvais')),
                type_activite VARCHAR(30) NOT NULL,
                conseil TEXT NOT NULL,
                niveau_urgence INTEGER DEFAULT 1 CHECK (niveau_urgence BETWEEN 1 AND 5),
                icone VARCHAR(20) DEFAULT 'info',
                actif BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'recommandations_base' créée")
        
        # Création des index pour performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_profils_commune ON profils_utilisateurs(commune_residence);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_profils_type ON profils_utilisateurs(type_profil);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_seuils_profil_polluant ON seuils_personnalises(profil_type, polluant);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommandations_profil_niveau ON recommandations_base(profil_cible, niveau_pollution);")
        
        print("✅ Index de performance créés")
        
        conn.commit()
        print("\n🎉 SUCCÈS : Toutes les tables ont été créées avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables : {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_profils_tables()