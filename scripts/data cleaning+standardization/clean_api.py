import json
import os
from datetime import datetime

def create_output_directory():
    """Créer le dossier de sortie pour les fichiers nettoyés"""
    output_dir = os.path.join('..', 'data', 'api-epis_pollution_cleaned')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Dossier créé : {output_dir}")
    return output_dir

def remove_duplicates(features):
    """Supprimer les doublons basés sur plusieurs critères"""
    seen = set()
    unique_features = []
    duplicates_count = 0
    
    for feature in features:
        props = feature.get('properties', {})
        
        # Créer une clé unique basée sur plusieurs champs
        key = (
            props.get('aasqa', ''),
            props.get('date_ech', ''),
            props.get('lib_zone', ''),
            props.get('etat', ''),
            props.get('code_zone', '')
        )
        
        if key not in seen:
            seen.add(key)
            unique_features.append(feature)
        else:
            duplicates_count += 1
    
    return unique_features, duplicates_count

def optimize_coordinates(features):
    """Optimiser les coordonnées (arrondir pour réduire la précision)"""
    for feature in features:
        coords = feature.get('geometry', {}).get('coordinates', [])
        if coords and len(coords) == 2:
            try:
                # Vérifier que les coordonnées sont des nombres
                if isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
                    # Arrondir à 6 décimales (précision ~10cm)
                    feature['geometry']['coordinates'] = [
                        round(float(coords[0]), 6),
                        round(float(coords[1]), 6)
                    ]
            except (TypeError, ValueError):
                # Garder les coordonnées originales si erreur de conversion
                pass
    return features

def clean_json_file(input_filepath, output_dir):
    """Nettoyer un fichier JSON individuel"""
    filename = os.path.basename(input_filepath)
    pollutant = filename.replace('data_', '').replace('.json', '').upper()
    
    print(f"\n🔧 NETTOYAGE DE {pollutant}")
    print("-" * 40)
    
    try:
        # Charger les données
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_features = data.get('features', [])
        original_size = os.path.getsize(input_filepath) / 1024 / 1024  # MB
        
        print(f"📊 Données originales : {len(original_features)} entrées ({original_size:.2f} MB)")
        
        # Étapes de nettoyage
        features = original_features.copy()
        
        # 1. Supprimer les doublons
        features, duplicates_removed = remove_duplicates(features)
        print(f"🔄 Doublons supprimés : {duplicates_removed}")
        
        # 2. Optimiser les coordonnées
        features = optimize_coordinates(features)
        
        # Créer les nouvelles données
        cleaned_data = {
            'type': data.get('type', 'FeatureCollection'),
            'name': data.get('name', ''),
            'crs': data.get('crs', {}),
            'features': features
        }
        
        # Sauvegarder le fichier nettoyé
        output_filepath = os.path.join(output_dir, f'cleaned_{filename}')
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, separators=(',', ':'))
        
        # Statistiques finales
        new_size = os.path.getsize(output_filepath) / 1024 / 1024  # MB
        reduction_percent = ((original_size - new_size) / original_size) * 100 if original_size > 0 else 0
        
        print(f"✅ Données nettoyées : {len(features)} entrées ({new_size:.2f} MB)")
        print(f"💾 Réduction de taille : {reduction_percent:.1f}%")
        print(f"📁 Sauvegardé dans : {output_filepath}")
        
        return {
            'pollutant': pollutant,
            'original_entries': len(original_features),
            'cleaned_entries': len(features),
            'original_size_mb': original_size,
            'cleaned_size_mb': new_size,
            'duplicates_removed': duplicates_removed,
            'reduction_percent': reduction_percent,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage de {pollutant}: {e}")
        return {
            'pollutant': pollutant,
            'original_entries': 0,
            'cleaned_entries': 0,
            'original_size_mb': 0,
            'cleaned_size_mb': 0,
            'duplicates_removed': 0,
            'reduction_percent': 0,
            'success': False,
            'error': str(e)
        }

def generate_cleaning_report(results, output_dir):
    """Générer un rapport de nettoyage"""
    report_path = os.path.join(output_dir, 'rapport_nettoyage.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("RAPPORT DE NETTOYAGE - API EPISODES POLLUTION\n")
        f.write("=" * 60 + "\n")
        f.write(f"Date de nettoyage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total_original_size = 0
        total_cleaned_size = 0
        total_original_entries = 0
        total_cleaned_entries = 0
        total_duplicates = 0
        successful_cleanings = 0
        
        for result in results:
            if result['success']:
                successful_cleanings += 1
                f.write(f"POLLUANT : {result['pollutant']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Entrées originales : {result['original_entries']}\n")
                f.write(f"Entrées nettoyées : {result['cleaned_entries']}\n")
                f.write(f"Doublons supprimés : {result['duplicates_removed']}\n")
                f.write(f"Taille originale : {result['original_size_mb']:.2f} MB\n")
                f.write(f"Taille nettoyée : {result['cleaned_size_mb']:.2f} MB\n")
                f.write(f"Réduction : {result['reduction_percent']:.1f}%\n\n")
                
                total_original_size += result['original_size_mb']
                total_cleaned_size += result['cleaned_size_mb']
                total_original_entries += result['original_entries']
                total_cleaned_entries += result['cleaned_entries']
                total_duplicates += result['duplicates_removed']
            else:
                f.write(f"ERREUR - POLLUANT : {result['pollutant']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Erreur : {result.get('error', 'Erreur inconnue')}\n\n")
        
        f.write("RÉSUMÉ GLOBAL\n")
        f.write("=" * 30 + "\n")
        f.write(f"Fichiers traités avec succès : {successful_cleanings}\n")
        f.write(f"Total entrées originales : {total_original_entries}\n")
        f.write(f"Total entrées nettoyées : {total_cleaned_entries}\n")
        f.write(f"Total doublons supprimés : {total_duplicates}\n")
        f.write(f"Taille totale originale : {total_original_size:.2f} MB\n")
        f.write(f"Taille totale nettoyée : {total_cleaned_size:.2f} MB\n")
        if total_original_size > 0:
            f.write(f"Réduction totale : {((total_original_size - total_cleaned_size) / total_original_size) * 100:.1f}%\n")
        else:
            f.write("Réduction totale : 0.0%\n")
    
    print(f"\n📋 Rapport de nettoyage sauvegardé : {report_path}")

def main():
    """Fonction principale de nettoyage"""
    print("🚀 SCRIPT DE NETTOYAGE - API EPISODES POLLUTION")
    print("=" * 60)
    
    # Créer le dossier de sortie
    try:
        output_dir = create_output_directory()
        print(f"✅ Dossier de sortie configuré : {output_dir}")
    except Exception as e:
        print(f"❌ Erreur création dossier sortie : {e}")
        return
    
    # Dossier source
    source_dir = os.path.join('..', 'data', 'api-epis_pollution-01-01-2024_01-01-2025')
    print(f"📂 Recherche dossier source : {source_dir}")
    
    # Vérifier que le dossier source existe
    if not os.path.exists(source_dir):
        print(f"❌ Dossier source non trouvé : {source_dir}")
        # Essayer le chemin absolu
        abs_source_dir = os.path.abspath(source_dir)
        print(f"📂 Chemin absolu testé : {abs_source_dir}")
        return
    
    print(f"✅ Dossier source trouvé : {source_dir}")
    
    # Fichiers à traiter
    files_to_clean = [
        'data_no2.json',
        'data_o3.json', 
        'data_pm10.json',
        'data_pm25.json'
        # data_so2.json exclu car données insuffisantes
    ]
    
    print(f"\n📁 Dossier sortie : {output_dir}")
    print(f"📋 Fichiers à traiter : {len(files_to_clean)}")
    
    # Lister les fichiers dans le dossier source
    try:
        source_files = os.listdir(source_dir)
        print(f"📄 Fichiers dans le dossier source : {source_files}")
    except Exception as e:
        print(f"❌ Erreur lecture dossier source : {e}")
        return
    
    results = []
    
    # Nettoyer chaque fichier
    for filename in files_to_clean:
        filepath = os.path.join(source_dir, filename)
        print(f"\n🔍 Vérification : {filepath}")
        if os.path.exists(filepath):
            print(f"✅ Fichier trouvé : {filename}")
            result = clean_json_file(filepath, output_dir)
            results.append(result)
        else:
            print(f"⚠️ Fichier non trouvé : {filepath}")
            results.append({
                'pollutant': filename.replace('data_', '').replace('.json', '').upper(),
                'original_entries': 0,
                'cleaned_entries': 0,
                'original_size_mb': 0,
                'cleaned_size_mb': 0,
                'duplicates_removed': 0,
                'reduction_percent': 0,
                'success': False,
                'error': 'Fichier non trouvé'
            })
    
    # Générer le rapport final
    print(f"\n📋 Génération du rapport...")
    generate_cleaning_report(results, output_dir)
    
    # Résumé final
    successful_results = [r for r in results if r['success']]
    
    print(f"\n🎉 NETTOYAGE TERMINÉ !")
    print(f"✅ Fichiers traités avec succès : {len(successful_results)}/{len(files_to_clean)}")
    print(f"📁 Fichiers nettoyés disponibles dans : {output_dir}")
    print(f"📋 Consultez le rapport détaillé : {os.path.join(output_dir, 'rapport_nettoyage.txt')}")

if __name__ == "__main__":
    main()
