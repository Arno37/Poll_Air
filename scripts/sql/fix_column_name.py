import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "database": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "port": os.getenv("PG_PORT")
}

def fix_column_name():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 CORRECTION DU NOM DE COLONNE")
        print("=" * 50)
        
        # 1. Supprimer l'ancienne FK (si elle existe)
        print("1️⃣ Suppression de l'ancienne contrainte FK...")
        cursor.execute("ALTER TABLE communes DROP CONSTRAINT IF EXISTS fk_communes_aasqa;")
          # 2. Renommer la colonne dans assqa_regions
        print("2️⃣ Renommage de la colonne: aasqa_code → assqa_code (dans assqa_regions)")
        cursor.execute("ALTER TABLE assqa_regions RENAME COLUMN aasqa_code TO assqa_code;")
        
        # 3. Recréer la FK avec le bon nom
        print("3️⃣ Recréation de la contrainte FK...")
        cursor.execute("""
            ALTER TABLE communes 
            ADD CONSTRAINT fk_communes_aasqa 
            FOREIGN KEY (assqa_code) 
            REFERENCES assqa_regions(assqa_code);
        """)
          # 4. Vérifier le résultat
        print("4️⃣ Vérification de la structure...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'assqa_regions' 
                AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        
        colonnes = cursor.fetchall()
        print("\n📋 Nouvelle structure de la table 'assqa_regions':")
        for col, dtype in colonnes:
            if col == 'assqa_code':
                print(f"  • {col} ({dtype}) ✅ CORRIGÉ")
            else:
                print(f"  • {col} ({dtype})")
        
        # Valider les changements
        conn.commit()
        print(f"\n🎉 SUCCÈS! Colonne renommée et FK recréée.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_column_name()
