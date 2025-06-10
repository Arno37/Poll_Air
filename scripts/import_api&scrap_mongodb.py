import os
import json
from datetime import datetime
from dotenv import load_dotenv
import pymongo

# Charger les variables d'environnement
load_dotenv()

def test_mongodb_connection():
    """Tester la connexion MongoDB"""
    try:
        connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        client.close()
        return True
    except ImportError:
        print("❌ pymongo n'est pas installé. Installez-le avec : pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ MongoDB non accessible : {e}")
        return False

def reorganize_mongodb_collections():
    """Réorganiser les collections MongoDB selon la nouvelle structure"""
    
    print("RÉORGANISATION DES COLLECTIONS MONGODB")
    print("=" * 60)
    
    if not test_mongodb_connection():
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGO_DATABASE', 'pollution_app')
    
    print(f"🔗 Connexion : {connection_string}")
    print(f"🗃️ Base de données : {database_name}")
    
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    # Lister les collections existantes
    existing_collections = db.list_collection_names()
    print(f"\n📊 Collections existantes : {len(existing_collections)}")
    for col in existing_collections:
        count = db[col].count_documents({})
        print(f"   - {col}: {count} documents")
    
    print(f"\n" + "=" * 60)
    print("CRÉATION DES NOUVELLES COLLECTIONS")
    print("=" * 60)
    
    # ===== 1. COLLECTION POLLUTION (données scraping) =====
    print(f"\n📈 1. Création de la collection POLLUTION")
    print("-" * 50)
    
    pollution_collection = db["POLLUTION"]
    
    # Supprimer la collection existante si elle existe
    if "POLLUTION" in existing_collections:
        pollution_collection.drop()
        print("   🗑️ Collection POLLUTION existante supprimée")
    
    # Rassembler toutes les données scraping
    pollution_documents = []
    scraping_collections = [col for col in existing_collections if col.startswith('scraping_')]
    
    total_pollution_docs = 0
    for col_name in scraping_collections:
        collection = db[col_name]
        docs = list(collection.find({}))
        
        print(f"   📂 Migration {col_name}: {len(docs)} documents")
        
        for doc in docs:
            # Nettoyer et restructurer le document
            pollution_doc = {
                "_id": doc.get("_id"),
                "type_donnee": "moyenne_journaliere",
                "source": "scraping_moy_journaliere",
                "polluant": doc.get("polluant", "").upper(),
                "import_date": doc.get("import_date", datetime.now()),
                "cleaning_status": "cleaned",
                
                # Informations temporelles
                "date_debut": doc.get("date_debut"),
                "date_fin": doc.get("date_fin"),
                
                # Informations géographiques
                "organisme": doc.get("organisme"),
                "code_zas": doc.get("code_zas"),
                "zas": doc.get("zas"),
                "code_site": doc.get("code_site"),
                "nom_site": doc.get("nom_site"),
                "latitude": doc.get("latitude"),
                "longitude": doc.get("longitude"),
                
                # Informations de mesure
                "type_implantation": doc.get("type_implantation"),
                "type_influence": doc.get("type_influence"),
                "reglementaire": doc.get("reglementaire"),
                "type_evaluation": doc.get("type_evaluation"),
                "type_valeur": doc.get("type_valeur"),
                
                # Valeurs de pollution
                "valeur": doc.get("valeur"),
                "valeur_brute": doc.get("valeur_brute"),
                "unite_mesure": doc.get("unite_mesure"),
                
                # Informations qualité
                "taux_saisie": doc.get("taux_saisie"),
                "couverture_temporelle": doc.get("couverture_temporelle"),
                "couverture_donnees": doc.get("couverture_donnees"),
                "code_qualite": doc.get("code_qualite"),
                "validite": doc.get("validite"),
                
                # Données brutes pour référence
                "raw_data": doc.get("raw_data", {})
            }
            
            pollution_documents.append(pollution_doc)
        
        total_pollution_docs += len(docs)
    
    # Insérer dans la nouvelle collection POLLUTION
    if pollution_documents:
        try:
            result = pollution_collection.insert_many(pollution_documents, ordered=False)
            print(f"   ✅ {len(result.inserted_ids)} documents insérés dans POLLUTION")
        except Exception as e:
            print(f"   ⚠️ Erreur insertion POLLUTION: {e}")
            # Insertion un par un en cas d'erreur
            inserted = 0
            for doc in pollution_documents:
                try:
                    pollution_collection.insert_one(doc)
                    inserted += 1
                except:
                    pass
            print(f"   ✅ {inserted} documents insérés dans POLLUTION (un par un)")
    
    # ===== 2. COLLECTION EPIS_POLLUTION (données API) =====
    print(f"\n🔬 2. Création de la collection EPIS_POLLUTION")
    print("-" * 50)
    
    epis_collection = db["EPIS_POLLUTION"]
    
    # Supprimer la collection existante si elle existe
    if "EPIS_POLLUTION" in existing_collections:
        epis_collection.drop()
        print("   🗑️ Collection EPIS_POLLUTION existante supprimée")
    
    # Rassembler toutes les données API (épisodes)
    epis_documents = []
    api_collections = [col for col in existing_collections if col.startswith('pollution_')]
    
    total_epis_docs = 0
    for col_name in api_collections:
        collection = db[col_name]
        docs = list(collection.find({}))
        
        print(f"   📂 Migration {col_name}: {len(docs)} documents")
        
        for doc in docs:
            # Nettoyer et restructurer le document
            epis_doc = {
                "_id": f"epis_{doc.get('_id', '')}",
                "type_donnee": "episode_pollution",
                "source": "api_epis_cleaned",
                "polluant": doc.get("polluant", "").upper(),
                "import_date": doc.get("import_date", datetime.now()),
                "cleaning_status": "cleaned",
                
                # Informations épisodes
                "feature_id": doc.get("feature_id"),
                "aasqa": doc.get("aasqa"),
                "date_ech": doc.get("date_ech"),
                "date_maj": doc.get("date_maj"),
                "lib_pol": doc.get("lib_pol"),
                "lib_zone": doc.get("lib_zone"),
                "etat": doc.get("etat"),
                "code_zone": doc.get("code_zone"),
                "code_pol": doc.get("code_pol"),
                
                # Coordonnées géographiques
                "latitude": doc.get("latitude"),
                "longitude": doc.get("longitude"),
                
                # Données complètes
                "properties": doc.get("properties", {}),
                "geometry": doc.get("geometry", {})
            }
            
            epis_documents.append(epis_doc)
        
        total_epis_docs += len(docs)
    
    # Insérer dans la nouvelle collection EPIS_POLLUTION
    if epis_documents:
        try:
            result = epis_collection.insert_many(epis_documents, ordered=False)
            print(f"   ✅ {len(result.inserted_ids)} documents insérés dans EPIS_POLLUTION")
        except Exception as e:
            print(f"   ⚠️ Erreur insertion EPIS_POLLUTION: {e}")
            # Insertion un par un en cas d'erreur
            inserted = 0
            for doc in epis_documents:
                try:
                    epis_collection.insert_one(doc)
                    inserted += 1
                except:
                    pass
            print(f"   ✅ {inserted} documents insérés dans EPIS_POLLUTION (un par un)")
    
    # ===== 3. CRÉATION DES INDEX =====
    print(f"\n🔍 3. Création des index")
    print("-" * 50)
    
    try:
        # Index pour POLLUTION
        pollution_collection.create_index([("polluant", 1), ("date_debut", 1)])
        pollution_collection.create_index([("nom_site", 1)])
        pollution_collection.create_index([("organisme", 1)])
        pollution_collection.create_index([("valeur", 1)])
        pollution_collection.create_index([("latitude", 1), ("longitude", 1)])
        pollution_collection.create_index([("type_donnee", 1)])
        print("   ✅ Index créés pour POLLUTION")
        
        # Index pour EPIS_POLLUTION
        epis_collection.create_index([("polluant", 1), ("date_ech", 1)])
        epis_collection.create_index([("lib_zone", 1)])
        epis_collection.create_index([("etat", 1)])
        epis_collection.create_index([("aasqa", 1)])
        epis_collection.create_index([("latitude", 1), ("longitude", 1)])
        epis_collection.create_index([("type_donnee", 1)])
        print("   ✅ Index créés pour EPIS_POLLUTION")
        
    except Exception as e:
        print(f"   ⚠️ Erreur création index: {e}")
    
    # ===== 4. SUPPRESSION DES ANCIENNES COLLECTIONS (OPTIONNEL) =====
    print(f"\n🗑️ 4. Nettoyage des anciennes collections")
    print("-" * 50)
    
    # Demander confirmation avant suppression
    old_collections = [col for col in existing_collections if col.startswith(('pollution_', 'scraping_'))]
    
    print(f"   Collections à supprimer : {old_collections}")
    print("   💡 Ces collections vont être supprimées car les données sont maintenant dans POLLUTION et EPIS_POLLUTION")
    
    for col_name in old_collections:
        try:
            db[col_name].drop()
            print(f"   🗑️ {col_name} supprimée")
        except Exception as e:
            print(f"   ⚠️ Erreur suppression {col_name}: {e}")
    
    # ===== 5. RÉSUMÉ FINAL =====
    print(f"\n" + "=" * 60)
    print("RÉORGANISATION TERMINÉE")
    print("=" * 60)
    
    # Vérification finale
    pollution_count = pollution_collection.count_documents({})
    epis_count = epis_collection.count_documents({})
    
    print(f"✅ Collection POLLUTION : {pollution_count:,} documents")
    print(f"✅ Collection EPIS_POLLUTION : {epis_count:,} documents")
    print(f"✅ Total documents : {pollution_count + epis_count:,}")
    
    # Statistiques par polluant
    print(f"\n📊 Répartition par polluant dans POLLUTION:")
    pipeline = [
        {"$group": {"_id": "$polluant", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    for result in pollution_collection.aggregate(pipeline):
        print(f"   - {result['_id']}: {result['count']:,} documents")
    
    print(f"\n📊 Répartition par polluant dans EPIS_POLLUTION:")
    for result in epis_collection.aggregate(pipeline):
        print(f"   - {result['_id']}: {result['count']:,} documents")
    
    client.close()
    print(f"\n🎉 Réorganisation terminée avec succès !")

if __name__ == "__main__":
    reorganize_mongodb_collections()
