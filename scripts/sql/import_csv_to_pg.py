import os
import pandas as pd
import psycopg2
from psycopg2 import sql

def import_recommandations_base(cur, df):
    for _, row in df.iterrows():
        cur.execute('''
            INSERT INTO recommandations_base (profil_cible, niveau_pollution, type_activite, conseil, niveau_urgence, icone, actif, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['profil_cible'],
            row['niveau_pollution'],
            row['type_activite'],
            row['conseil'],
            int(row['niveau_urgence']) if not pd.isna(row['niveau_urgence']) else None,
            row['icone'],
            bool(row['actif']) if not pd.isna(row['actif']) else True,
            row['created_at'] if not pd.isna(row['created_at']) else None
        ))

def import_seuils_personnalises(cur, df):
    for _, row in df.iterrows():
        cur.execute('''
            INSERT INTO seuils_personnalises (profil_type, polluant, seuil_info, seuil_alerte, pourcentage_reduction, conseil_depassement)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            row['profil_type'],
            row['polluant'],
            int(row['seuil_info']),
            int(row['seuil_alerte']),
            int(row['pourcentage_reduction']),
            row['conseil_depassement']
        ))

def main():
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST', 'localhost'),
        database=os.getenv('PG_DATABASE', 'postgres'),
        user=os.getenv('PG_USER', 'postgres'),
        password=os.getenv('PG_PASSWORD', ''),
        port=os.getenv('PG_PORT', '5432')
    )
    cur = conn.cursor()
    # Import recommandations_base
    df1 = pd.read_csv('data/recommandations_base.csv')
    import_recommandations_base(cur, df1)
    # Import seuils_personnalises
    df2 = pd.read_csv('data/seuils_personnalises.csv')
    import_seuils_personnalises(cur, df2)
    conn.commit()
    cur.close()
    conn.close()
    print('Import CSV terminé.')

if __name__ == "__main__":
    main()
