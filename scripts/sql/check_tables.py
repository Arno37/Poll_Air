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

try:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    print("🔍 LISTE DE TOUTES LES TABLES")
    print("=" * 50)
    
    # Lister toutes les tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print("📋 Tables trouvées :")
        for (table_name,) in tables:
            print(f"  • {table_name}")
            
        # Chercher des tables avec "aasqa" ou "assqa" dans le nom
        print(f"\n🔍 Tables contenant 'aasqa' ou 'assqa' :")
        for (table_name,) in tables:
            if 'aasqa' in table_name.lower() or 'assqa' in table_name.lower():
                print(f"  🎯 {table_name}")
                
                # Afficher la structure de cette table
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                        AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """)
                
                colonnes = cursor.fetchall()
                for col, dtype in colonnes:
                    print(f"     • {col} ({dtype})")
    else:
        print("❌ Aucune table trouvée")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
