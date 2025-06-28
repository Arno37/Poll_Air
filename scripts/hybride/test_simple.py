"""
Test ultra-simple de récupération de données PostgreSQL et MongoDB
Affiche juste quelques enregistrements de chaque base dans la console
"""

import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le dossier parent
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

def test_postgresql():
    """Test connexion et récupération PostgreSQL"""
    print("🔄 Test PostgreSQL...")
    
    try:
        # Configuration depuis les variables d'environnement (comme vos autres scripts)
        DATABASE_CONFIG = {
            "host": os.getenv("PG_HOST", "localhost"),
            "database": os.getenv("PG_DATABASE", "postgres"),  # Selon votre .env
            "user": os.getenv("PG_USER", "postgres"),  
            "password": os.getenv("PG_PASSWORD", ""),
            "port": int(os.getenv("PG_PORT", "5432"))
        }
        
        print(f"   Connexion à: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
        
        # Connexion PostgreSQL
        conn = psycopg2.connect(**DATABASE_CONFIG)
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Test simple : récupérer 5 enregistrements de la table consolidée
        cursor.execute("""
            SELECT * FROM indices_qualite_air_consolides 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        
        print(f"✅ PostgreSQL - {len(results)} enregistrements récupérés:")
        for i, row in enumerate(results, 1):
            print(f"  {i}. {dict(row)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False

def test_mongodb():
    """Test connexion et récupération MongoDB"""
    print("\n🔄 Test MongoDB...")
    
    try:
        # Connexion MongoDB avec la bonne base depuis .env
        mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
        mongo_db_name = os.getenv('MONGO_DATABASE', 'pollution')
        
        print(f"   Connexion MongoDB: {mongo_uri} → base '{mongo_db_name}'")
        
        client = MongoClient(mongo_uri)
        
        # Lister toutes les bases disponibles
        all_dbs = client.list_database_names()
        print(f"📋 Bases MongoDB disponibles: {all_dbs}")
        
        db = client[mongo_db_name]
        
        # Lister toutes les collections disponibles
        collections = db.list_collection_names()
        print(f"📋 Collections MongoDB disponibles: {collections}")
        
        # Test collection épisodes pollution
        collection_episodes = db["EPIS_POLLUTION"]
        episodes_count = collection_episodes.count_documents({})
        episodes = list(collection_episodes.find().limit(3))
        
        print(f"✅ MongoDB Episodes - {len(episodes)} enregistrements récupérés (total: {episodes_count}):")
        for i, episode in enumerate(episodes, 1):
            # Afficher juste les infos principales
            props = episode.get('properties', {})
            print(f"  {i}. Zone: {props.get('code_insee', 'N/A')}, "
                  f"Polluant: {props.get('polluant', 'N/A')}, "
                  f"Niveau: {props.get('niveau', 'N/A')}")
        
        # Test collection moyennes journalières
        print(f"\n🔄 Test collection moyennes journalières...")
        collection_moyennes = db["MOY_JOURNALIERE"]
        moyennes_count = collection_moyennes.count_documents({})
        moyennes = list(collection_moyennes.find().limit(3))
        
        print(f"✅ MongoDB Moyennes - {len(moyennes)} enregistrements récupérés (total: {moyennes_count}):")
        for i, moyenne in enumerate(moyennes, 1):
            props = moyenne.get('properties', {})
            print(f"  {i}. Zone: {props.get('code_insee', 'N/A')}, "
                  f"Polluant: {props.get('polluant', 'N/A')}, "
                  f"Valeur: {props.get('valeur', 'N/A')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        return False

def test_complet():
    """Test complet des deux bases"""
    print("🚀 Test ultra-simple de récupération de données")
    print("=" * 50)
    
    # Test PostgreSQL
    pg_ok = test_postgresql()
    
    # Test MongoDB  
    mongo_ok = test_mongodb()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU TEST:")
    print(f"  PostgreSQL: {'✅ OK' if pg_ok else '❌ ÉCHEC'}")
    print(f"  MongoDB: {'✅ OK' if mongo_ok else '❌ ÉCHEC'}")
    
    if pg_ok and mongo_ok:
        print("\n🎉 Les deux bases sont accessibles et contiennent des données !")
    else:
        print("\n⚠️  Vérifiez les connexions aux bases de données.")
        if not pg_ok:
            print("   - PostgreSQL: Vérifiez que le service est démarré et les paramètres de connexion")
        if not mongo_ok:
            print("   - MongoDB: Vérifiez que le service est démarré et les collections existent")

if __name__ == "__main__":
    test_complet()
