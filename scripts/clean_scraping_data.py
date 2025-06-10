#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour nettoyer les données scraping-moy_journaliere
Ces fichiers contiennent des données CSV encapsulées dans du JSON
avec des structures problématiques à corriger.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def parse_csv_line(csv_line, headers):
    """Parse une ligne CSV et retourne un dictionnaire structuré."""
    values = csv_line.split(';')
    
    if len(values) != len(headers):
        print(f"⚠️  Nombre de colonnes incorrect: {len(values)} vs {len(headers)}")
        return None
    
    result = {}
    for i, header in enumerate(headers):
        value = values[i].strip()
        
        # Conversion des types appropriés
        if header in ['valeur', 'valeur brute', 'taux de saisie', 'couverture temporelle', 
                     'couverture de données', 'Latitude', 'Longitude']:
            try:
                result[header] = float(value) if '.' in value else int(value)
            except ValueError:
                result[header] = value
        elif header in ['validité']:
            try:
                result[header] = int(value)
            except ValueError:
                result[header] = value
        else:
            result[header] = value
    
    return result

def clean_headers(header_string):
    """Nettoie et standardise les en-têtes CSV."""
    # Enlève le BOM et les caractères indésirables
    header_string = header_string.replace('\ufeff', '').strip()
    headers = [h.strip() for h in header_string.split(';')]
    
    # Standardise les noms de colonnes
    header_mapping = {
        'Date de début': 'date_debut',
        'Date de fin': 'date_fin',
        'Organisme': 'organisme',
        'code zas': 'code_zas',
        'Zas': 'zas',
        'code site': 'code_site',
        'nom site': 'nom_site',
        'type d\'implantation': 'type_implantation',
        'Polluant': 'polluant',
        'type d\'influence': 'type_influence',
        'Réglementaire': 'reglementaire',
        'type d\'évaluation': 'type_evaluation',
        'type de valeur': 'type_valeur',
        'valeur': 'valeur',
        'valeur brute': 'valeur_brute',
        'unité de mesure': 'unite_mesure',
        'taux de saisie': 'taux_saisie',
        'couverture temporelle': 'couverture_temporelle',
        'couverture de données': 'couverture_donnees',
        'code qualité': 'code_qualite',
        'validité': 'validite',
        'Latitude': 'latitude',
        'Longitude': 'longitude'
    }
    
    standardized_headers = []
    for header in headers:
        standardized_headers.append(header_mapping.get(header, header))
    
    return standardized_headers

def clean_file(input_path, output_path):
    """Nettoie un fichier de données scraping."""
    print(f"🔄 Nettoyage de {input_path.name}...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print(f"⚠️  Fichier vide: {input_path.name}")
        return 0
    
    # Récupère les en-têtes du premier objet
    first_key = list(data[0].keys())[0]
    headers = clean_headers(first_key)
    
    cleaned_data = []
    duplicates = 0
    errors = 0
    seen_records = set()
    
    for item in data:
        key = list(item.keys())[0]
        csv_line = item[key]
        
        # Parse la ligne CSV
        parsed_data = parse_csv_line(csv_line, headers)
        if parsed_data is None:
            errors += 1
            continue
        
        # Ajoute des métadonnées
        parsed_data['source'] = 'scraping-moy_journaliere'
        parsed_data['polluant_type'] = input_path.stem
        parsed_data['import_date'] = datetime.now().isoformat()
        
        # Crée une clé unique pour détecter les doublons
        unique_key = f"{parsed_data.get('code_site', '')}_{parsed_data.get('date_debut', '')}_{parsed_data.get('polluant', '')}"
        
        if unique_key in seen_records:
            duplicates += 1
            continue
        
        seen_records.add(unique_key)
        cleaned_data.append(parsed_data)
    
    # Sauvegarde les données nettoyées
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {input_path.name}: {len(cleaned_data)} enregistrements nettoyés")
    print(f"   📊 Doublons supprimés: {duplicates}")
    print(f"   ⚠️  Erreurs de parsing: {errors}")
    
    return len(cleaned_data)

def main():
    """Fonction principale."""
    # Chemins des dossiers
    input_dir = Path("c:/Users/mpadmin/Documents/PM/data/scraping-moy_journaliere")
    output_dir = Path("c:/Users/mpadmin/Documents/PM/data/scraping-moy_journaliere_cleaned")
    
    if not input_dir.exists():
        print(f"❌ Dossier source introuvable: {input_dir}")
        sys.exit(1)
    
    # Crée le dossier de sortie
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 Début du nettoyage des données scraping-moy_journaliere")
    print(f"📂 Source: {input_dir}")
    print(f"📂 Destination: {output_dir}")
    print("-" * 60)
    
    total_records = 0
    
    # Traite chaque fichier JSON
    for json_file in input_dir.glob("*.json"):
        output_file = output_dir / json_file.name
        records_count = clean_file(json_file, output_file)
        total_records += records_count
    
    print("-" * 60)
    print(f"✅ Nettoyage terminé!")
    print(f"📊 Total des enregistrements nettoyés: {total_records}")
    print(f"📂 Fichiers sauvegardés dans: {output_dir}")

if __name__ == "__main__":
    main()
