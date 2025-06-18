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
    
    print("🔍 STRUCTURE DES TABLES")
    print("=" * 50)
    
    # Vérifier colonnes de chaque table
    tables = ['communes', 'aasqa_regions', 'polluants', 'indice', 'qualite_air']
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' 
                AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        
        colonnes = cursor.fetchall()
        if colonnes:
            for col, dtype in colonnes:
                print(f"  • {col} ({dtype})")
        else:
            print(f"  ❌ Table '{table}' n'existe pas ou est vide")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
