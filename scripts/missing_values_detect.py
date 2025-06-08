import os
import pandas as pd
import numpy as np

def validate_data_quality(dossier_nettoyes="../data/file-indices_nettoyes"):
    """
    Vérifie la qualité des données : valeurs manquantes, nulles, vides
    """
    print("🔍 VALIDATION DE LA QUALITÉ DES DONNÉES")
    print("=" * 50)
    
    total_files = 0
    files_with_issues = 0
    
    for fichier in os.listdir(dossier_nettoyes):
        if fichier.endswith(".csv"):
            total_files += 1
            chemin = os.path.join(dossier_nettoyes, fichier)
            print(f"\n📄 Analyse de : {fichier}")
            
            df = pd.read_csv(chemin)
            has_issues = False
            
            # 1. Vérifier les valeurs nulles/NaN
            null_counts = df.isnull().sum()
            if null_counts.sum() > 0:
                has_issues = True
                print("❌ Valeurs NULL/NaN détectées :")
                for col, count in null_counts[null_counts > 0].items():
                    print(f"   - {col}: {count} valeurs manquantes")
            
            # 2. Vérifier les chaînes vides
            for col in df.select_dtypes(include=['object']).columns:
                empty_strings = (df[col] == '').sum()
                whitespace_only = df[col].astype(str).str.strip().eq('').sum()
                if empty_strings > 0 or whitespace_only > 0:
                    has_issues = True
                    print(f"❌ Chaînes vides dans '{col}': {empty_strings} vides, {whitespace_only} espaces")
            
            # 3. Vérifier les valeurs "nan" en texte
            for col in df.columns:
                nan_text = df[col].astype(str).str.lower().isin(['nan', 'null', 'none', 'n/a', '#n/a']).sum()
                if nan_text > 0:
                    has_issues = True
                    print(f"❌ Valeurs texte invalides dans '{col}': {nan_text}")
            
            # 4. Statistiques générales
            print(f"📊 Statistiques : {len(df)} lignes, {len(df.columns)} colonnes")
            
            if has_issues:
                files_with_issues += 1
                print("⚠️  Ce fichier contient des données manquantes")
            else:
                print("✅ Aucun problème détecté")
    
    # Résumé final
    print("\n" + "=" * 50)
    print(f"📈 RÉSUMÉ DE LA VALIDATION")
    print(f"Total fichiers analysés : {total_files}")
    print(f"Fichiers avec problèmes : {files_with_issues}")
    print(f"Fichiers sans problème : {total_files - files_with_issues}")
    
    if files_with_issues == 0:
        print("🎉 Toutes les données sont propres !")
    else:
        print("⚠️  Des corrections sont nécessaires")
    
    return files_with_issues == 0

if __name__ == "__main__":
    validate_data_quality()