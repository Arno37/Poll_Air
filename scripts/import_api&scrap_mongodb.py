import os
import json
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def find_data_directory():
    """Trouver automatiquement le bon chemin vers les données"""
    possible_paths = [
        "data/api-epis_pollution_cleaned",      # Si exécuté depuis la racine
        "../data/api-epis_pollution_cleaned",   # Si exécuté depuis scripts/
        "../../data/api-epis_pollution_cleaned" # Au cas où
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Dossier trouvé : {path}")
            return path
    
    print("❌ Dossier de données non trouvé")
    return None

def import_episodes_to_mongo():
    """Importer les épisodes de pollution nettoyés dans MongoDB"""
    
    connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGO_DATABASE', 'pollution_app')
    
    print("🚨 IMPORT DES ÉPISODES DE POLLUTION (VERSION CORRIGÉE)")
    print("=" * 60)
    
    # Trouver le bon chemin
    episodes_dir = find_data_directory()
    if not episodes_dir:
        return
    
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    # Fichiers à importer
    episode_files = [
        "cleaned_data_no2.json",
        "cleaned_data_o3.json", 
        "cleaned_data_pm10.json",
        "cleaned_data_pm25.json"
    ]
    
    total_imported = 0
    
    for filename in episode_files:
        filepath = os.path.join(episodes_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Fichier non trouvé : {filepath}")
            continue
            
        print(f"📂 Traitement : {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire le polluant du nom de fichier
            polluant = filename.replace('cleaned_data_', '').replace('.json', '').upper()
            
            # Traiter les features
            features = data.get('features', [])
            print(f"   📊 {len(features)} épisodes trouvés")
            
            # Créer une collection temporaire pour ce polluant
            collection_name = f"episodes_{polluant.lower()}"
            collection = db[collection_name]
            
            # Vider la collection existante
            collection.drop()
            
            # Préparer les documents à insérer
            documents = []
            for i, feature in enumerate(features):
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                doc = {
                    "_id": f"episode_{polluant}_{i}",
                    "type_donnee": "episode_pollution",
                    "source": "api_epis_cleaned",
                    "polluant": polluant,
                    "import_date": datetime.now(),
                    
                    # Données de l'épisode
                    "aasqa": properties.get("aasqa"),
                    "date_maj": properties.get("date_maj"),
                    "lib_pol": properties.get("lib_pol"),
                    "lib_zone": properties.get("lib_zone"),
                    "etat": properties.get("etat"),
                    "date_ech": properties.get("date_ech"),
                    "date_dif": properties.get("date_dif"),
                    "code_zone": properties.get("code_zone"),
                    "code_pol": properties.get("code_pol"),
                    
                    # Géométrie
                    "geometry_type": geometry.get("type"),
                    "coordinates": coordinates,
                    "latitude": coordinates[1] if len(coordinates) >= 2 else None,
                    "longitude": coordinates[0] if len(coordinates) >= 2 else None,
                    
                    # Document original
                    "feature_original": feature
                }
                
                documents.append(doc)
            
            # Insérer les documents
            if documents:
                result = collection.insert_many(documents)
                imported_count = len(result.inserted_ids)
                print(f"   ✅ {imported_count} épisodes importés dans {collection_name}")
                total_imported += imported_count
            
        except Exception as e:
            print(f"   ❌ Erreur traitement {filename}: {e}")
    
    print(f"\n✅ IMPORT TERMINÉ : {total_imported} épisodes au total")
    
    # Lister les collections créées
    collections = [col for col in db.list_collection_names() if col.startswith('episodes_')]
    print(f"📊 Collections créées : {collections}")
    
    for col_name in collections:
        count = db[col_name].count_documents({})
        print(f"   - {col_name}: {count} documents")
    
    client.close()
    
    if total_imported > 0:
        print(f"\n🚀 ÉTAPE SUIVANTE :")
        print(f"   Maintenant exécutez : python import_api&scrap_mongodb.py")
        print(f"   Pour réorganiser en collections MOY_JOURNALIERE et EPIS_POLLUTION")

def group_episodes_to_epis():
    """Regrouper les 4 collections episodes_* dans EPIS_POLLUTION"""
    
    connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGO_DATABASE', 'pollution_app')
    
    print("🚨 REGROUPEMENT DES ÉPISODES DANS EPIS_POLLUTION")
    print("=" * 60)
    
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    # Lister les collections existantes
    all_collections = db.list_collection_names()
    episode_collections = [col for col in all_collections if col.startswith('episodes_')]
    
    print(f"📊 Collections épisodes trouvées : {episode_collections}")
    
    if not episode_collections:
        print("❌ Aucune collection episodes_* trouvée")
        return
    
    # Créer/vider la collection EPIS_POLLUTION
    epis_collection = db["EPIS_POLLUTION"]
    if "EPIS_POLLUTION" in all_collections:
        epis_collection.drop()
        print("🗑️ Ancienne collection EPIS_POLLUTION supprimée")
    
    # Regrouper toutes les collections episodes_*
    total_docs = 0
    
    for col_name in episode_collections:
        source_collection = db[col_name]
        docs = list(source_collection.find({}))
        
        print(f"📂 Migration {col_name} : {len(docs)} documents")
        
        # Insérer les documents dans EPIS_POLLUTION
        if docs:
            try:
                result = epis_collection.insert_many(docs)
                inserted_count = len(result.inserted_ids)
                print(f"   ✅ {inserted_count} documents migrés vers EPIS_POLLUTION")
                total_docs += inserted_count
            except Exception as e:
                print(f"   ❌ Erreur migration {col_name}: {e}")
                # Essayer un par un en cas d'erreur
                inserted = 0
                for doc in docs:
                    try:
                        epis_collection.insert_one(doc)
                        inserted += 1
                    except:
                        pass
                print(f"   ✅ {inserted} documents migrés un par un")
                total_docs += inserted
    
    # Créer des index pour optimiser les requêtes
    print("\n🔍 Création des index...")
    try:
        epis_collection.create_index([("polluant", 1)])
        epis_collection.create_index([("etat", 1)])
        epis_collection.create_index([("date_ech", 1)])
        epis_collection.create_index([("lib_zone", 1)])
        epis_collection.create_index([("aasqa", 1)])
        epis_collection.create_index([("latitude", 1), ("longitude", 1)])
        epis_collection.create_index([("type_donnee", 1)])
        print("✅ Index créés pour EPIS_POLLUTION")
    except Exception as e:
        print(f"⚠️ Erreur création index: {e}")
    
    # Supprimer les anciennes collections episodes_*
    print(f"\n🗑️ Suppression des collections sources...")
    for col_name in episode_collections:
        try:
            db[col_name].drop()
            print(f"   🗑️ {col_name} supprimée")
        except Exception as e:
            print(f"   ⚠️ Erreur suppression {col_name}: {e}")
    
    # Vérification finale
    final_count = epis_collection.count_documents({})
    print(f"\n✅ REGROUPEMENT TERMINÉ")
    print(f"📊 Collection EPIS_POLLUTION : {final_count:,} documents")
    
    # Statistiques par polluant
    print(f"\n📊 Répartition par polluant dans EPIS_POLLUTION :")
    try:
        pipeline = [
            {"$group": {"_id": "$polluant", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        for result in epis_collection.aggregate(pipeline):
            if result['_id']:
                print(f"   - {result['_id']}: {result['count']:,} documents")
    except Exception as e:
        print(f"   ⚠️ Erreur statistiques: {e}")
    
    # Statistiques par état
    print(f"\n🚨 Répartition par état d'épisode :")
    try:
        pipeline = [
            {"$group": {"_id": "$etat", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        for result in epis_collection.aggregate(pipeline):
            if result['_id']:
                print(f"   - {result['_id']}: {result['count']:,} épisodes")
    except Exception as e:
        print(f"   ⚠️ Erreur statistiques par état: {e}")
    
    client.close()
    print(f"\n🎉 Les épisodes sont maintenant regroupés dans EPIS_POLLUTION !")
    
    # Afficher l'état final des collections
    print(f"\n📋 ÉTAT FINAL DES COLLECTIONS :")
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    final_collections = db.list_collection_names()
    for col in sorted(final_collections):
        count = db[col].count_documents({})
        print(f"   - {col}: {count:,} documents")
    
    client.close()

if __name__ == "__main__":
    import_episodes_to_mongo()
    group_episodes_to_epis()