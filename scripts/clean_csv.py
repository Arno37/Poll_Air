import os
import pandas as pd

dossier_source = "../data/file-indices_qualite_air-01-01-2024_01-01-2025"
dossier_sortie = "../data/file-indices_nettoyes"
os.makedirs(dossier_sortie, exist_ok=True)

colonnes_a_supprimer = [
    "date_maj", "code_zone", "coul_qual", "date_ech",
    "epsg_reg", "x_reg", "x_wgs84", "y_reg", "y_wgs84", "gml_id2"
    # code_so2 RETIRÉ de la liste - on le garde !
]

nouveaux_noms = [
    "aasqa", "NO2", "O3", "PM10", "PM25", "SO2",  # AJOUT de SO2
    "date_prise_mesure", "qualite_air", "zone", "source", "type_zone"
]

for fichier in os.listdir(dossier_source):
    if fichier.endswith(".csv"):
        chemin = os.path.join(dossier_source, fichier)
        print(f"Nettoyage de {chemin} ...")
        df = pd.read_csv(chemin)
        
        # Supprimer les colonnes indésirables
        colonnes_presentes = [col for col in colonnes_a_supprimer if col in df.columns]
        df = df.drop(columns=colonnes_presentes)
        print(f"Colonnes supprimées : {colonnes_presentes}")
        
        # Supprimer la 6e colonne (index 5) si elle existe encore
        if len(df.columns) > 6:
            colonne_supprimee = df.columns[6]  # Maintenant c'est la 7e colonne (index 6)
            df = df.drop(df.columns[6], axis=1)
            print(f"7e colonne '{colonne_supprimee}' supprimée pour : {fichier}")
        
        # Renommer les colonnes (maintenant 11 colonnes)
        if len(df.columns) == len(nouveaux_noms):
            df.columns = nouveaux_noms
            print(f"✅ Colonnes renommées pour : {fichier}")
        else:
            print(f"⚠️ Nombre de colonnes incorrect pour {fichier}: {len(df.columns)} colonnes trouvées, {len(nouveaux_noms)} attendues")
            print(f"Colonnes actuelles : {list(df.columns)}")
        
        # Pour les colonnes texte, supprimer les lignes avec des valeurs manquantes critiques
        critical_text_cols = ['aasqa', 'date_prise_mesure', 'zone']  # 'zone' est déjà inclus
        rows_before = len(df)
        for col in critical_text_cols:
            if col in df.columns:
                df = df.dropna(subset=[col])
        
        rows_after = len(df)
        if rows_before != rows_after:
            print(f"   - {rows_before - rows_after} lignes supprimées (données critiques manquantes)")
        
        # Pour les autres colonnes texte, remplacer par une valeur par défaut
        other_text_cols = ['qualite_air', 'source', 'type_zone']  # Retirer 'zone' d'ici
        for col in other_text_cols:
            if col in df.columns:
                df[col] = df[col].fillna("Inconnu")  # Remplacer par "Inconnu" ou une autre valeur par défaut
        
        chemin_sortie = os.path.join(dossier_sortie, fichier)
        df.to_csv(chemin_sortie, index=False)
        print(f"Fichier sauvegardé : {chemin_sortie}\n")

print("Tous les fichiers nettoyés sont dans le dossier file-indices_nettoyes.")