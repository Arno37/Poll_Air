import os
import json
import pymongo
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def import_api_epis_data():
    """
    Import simple des fichiers du dossier api-epis_pollution vers MongoDB
    """
    print("🚀 Import des données API EPIS vers MongoDB...")
    
    # Connexion MongoDB
    connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGO_DATABASE', 'pollution')
    
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    # Dossier source
    dossier_api = "../data/api-epis_pollution-01-01-2024_01-01-2025"
    
    if not os.path.exists(dossier_api):
        print(f"❌ Dossier introuvable : {dossier_api}")
        return
    
    print(f"📂 Lecture du dossier : {dossier_api}")
    
    # Parcourir tous les fichiers
    for fichier in os.listdir(dossier_api):
        chemin_fichier = os.path.join(dossier_api, fichier)
        
        if fichier.endswith('.json'):
            print(f"📄 Import de {fichier}...")
            
            try:
                # Lire le fichier JSON
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Nom de collection basé sur le fichier
                nom_collection = fichier.replace('.json', '_epis')
                collection = db[nom_collection]
                
                # Ajouter métadonnées d'import
                document = {
                    "source_file": fichier,
                    "import_date": datetime.now(),
                    "data_type": "geojson_epis",
                    "content": data
                }
                
                # Insérer le document
                result = collection.insert_one(document)
                print(f"✅ {fichier} importé dans collection '{nom_collection}'")
                print(f"   Document ID: {result.inserted_id}")
                
                # Si c'est un GeoJSON avec features, importer aussi chaque feature
                if isinstance(data, dict) and 'features' in data:
                    features_collection = db[f"{nom_collection}_features"]
                    features = data['features']
                    
                    # Ajouter métadonnées à chaque feature
                    for feature in features:
                        feature['source_file'] = fichier
                        feature['import_date'] = datetime.now()
                    
                    if features:
                        result = features_collection.insert_many(features)
                        print(f"   + {len(features)} features importées dans '{nom_collection}_features'")
                
            except Exception as e:
                print(f"❌ Erreur avec {fichier}: {e}")
        
        elif fichier.endswith('.csv'):
            print(f"📊 Fichier CSV détecté : {fichier} (ignoré pour cet import)")
        
        else:
            print(f"📁 Fichier ignoré : {fichier}")
    
    # Fermer connexion
    client.close()
    print("🎉 Import terminé !")

if __name__ == "__main__":
    import_api_epis_data()