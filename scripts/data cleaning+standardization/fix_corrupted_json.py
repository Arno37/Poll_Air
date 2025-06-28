import json
import re
import os
from pathlib import Path

def fix_corrupted_json_to_geojson(input_filepath, output_filepath=None):
    """
    Répare un fichier JSON corrompu et le convertit en GeoJSON valide
    """
    
    if output_filepath is None:
        output_filepath = input_filepath.replace('.json', '_fixed.json')
    
    print(f"🔧 Réparation du fichier: {os.path.basename(input_filepath)}")
    
    try:
        # Lire le fichier corrompu
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Taille du fichier: {len(content)} caractères")
        print(f"🔍 Début du contenu: {content[:200]}...")
        
        features = []
        
        # Si le contenu commence déjà par un tableau JSON
        if content.strip().startswith('['):
            try:
                # Essayer de parser directement comme un tableau de features
                data = json.loads(content)
                if isinstance(data, list):
                    features = data
                    print(f"✅ Tableau JSON détecté avec {len(features)} éléments")
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur de parsing du tableau: {e}")
        
        # Si c'est déjà un GeoJSON complet
        elif content.strip().startswith('{"type":"FeatureCollection"'):
            try:
                data = json.loads(content)
                if data.get('type') == 'FeatureCollection':
                    features = data.get('features', [])
                    print(f"✅ GeoJSON détecté avec {len(features)} features")
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur de parsing du GeoJSON: {e}")
        
        # Sinon, essayer de réparer le format corrompu
        else:
            # Pattern pour extraire les features complètes
            feature_pattern = r'(\{"type":"Feature".*?"geometry":\{"type":"Point","coordinates":\[[^\]]+\]\}\})'
            matches = re.findall(feature_pattern, content, re.DOTALL)
            
            print(f"🔍 Trouvé {len(matches)} features potentielles")
            
            for match in matches:
                try:
                    feature = json.loads(match.strip())
                    if (feature.get('type') == 'Feature' and 
                        'geometry' in feature and 
                        'properties' in feature):
                        features.append(feature)
                except json.JSONDecodeError:
                    continue
        
        # Créer la structure GeoJSON complète
        geojson = {
            "type": "FeatureCollection",
            "name": f"repaired_data_{os.path.basename(input_filepath).replace('.json', '')}",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::3857"
                }
            },
            "features": features
        }
        
        # Sauvegarder le fichier réparé
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier réparé avec {len(features)} features")
        print(f"📁 Sauvegardé: {output_filepath}")
        
        return len(features)
        
    except Exception as e:
        print(f"❌ Erreur lors de la réparation: {e}")
        return 0

def fix_all_corrupted_files(input_dir, output_dir):
    """
    Répare tous les fichiers JSON corrompus d'un dossier
    """
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    print(f"🔍 Recherche dans: {input_path.absolute()}")
    print(f"📁 Dossier existe: {input_path.exists()}")
    
    if not input_path.exists():
        print(f"❌ Le dossier {input_path} n'existe pas!")
        return 0, 0
    
    # Lister tous les fichiers JSON
    json_files = list(input_path.glob("*.json"))
    print(f"📋 Fichiers JSON trouvés: {len(json_files)}")
    
    for file in json_files:
        print(f"  - {file.name}")
    
    if not json_files:
        print("❌ Aucun fichier JSON trouvé!")
        return 0, 0
    
    # Créer le dossier de sortie
    output_path.mkdir(parents=True, exist_ok=True)
    
    total_features = 0
    files_processed = 0
    
    print("\n🚀 RÉPARATION DES FICHIERS JSON")
    print("=" * 50)
    
    # Traiter tous les fichiers JSON
    for json_file in json_files:
        output_file = output_path / f"fixed_{json_file.name}"
        
        features_count = fix_corrupted_json_to_geojson(
            str(json_file), 
            str(output_file)
        )
        
        if features_count > 0:
            total_features += features_count
            files_processed += 1
        
        print()
    
    # Rapport final
    print("📊 RAPPORT DE RÉPARATION")
    print("-" * 30)
    print(f"Fichiers traités: {files_processed}")
    print(f"Total features récupérées: {total_features}")
    
    return files_processed, total_features

if __name__ == "__main__":
    # Vérifier la structure des dossiers
    current_dir = Path.cwd()
    print(f"📍 Répertoire actuel: {current_dir}")
    
    # Chemins possibles
    possible_paths = [
        current_dir / ".." / ".." / "data" / "api-epis_pollution_cleaned",
        current_dir.parent.parent / "data" / "api-epis_pollution_cleaned",
        Path("C:/Users/mpadmin/Documents/PM/data/api-epis_pollution_cleaned"),
        current_dir / "data" / "api-epis_pollution_cleaned"
    ]
    
    input_directory = None
    for path in possible_paths:
        if path.exists():
            input_directory = str(path)
            break
    
    if input_directory is None:
        print("❌ Impossible de trouver le dossier des données!")
        print("🔍 Veuillez spécifier le chemin correct:")
        input_directory = input("Chemin vers les fichiers JSON: ").strip()
    
    output_directory = str(Path(input_directory).parent / "api-epis_pollution_fixed")
    
    print(f"📂 Dossier source: {input_directory}")
    print(f"📂 Dossier sortie: {output_directory}")
    
    # Réparer tous les fichiers
    fix_all_corrupted_files(input_directory, output_directory)