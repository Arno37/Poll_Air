import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def populate_seuils_personnalises():
    """Remplit la table seuils_personnalises avec les seuils adaptés par profil"""
    
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST'),
        database=os.getenv('PG_DATABASE'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        port=os.getenv('PG_PORT')
    )
    cursor = conn.cursor()
    
    try:
        print("📊 Insertion des seuils personnalisés...")
        
        # Données seuils personnalisés (réduction vs seuils réglementaires)
        seuils_data = [
            # SPORTIFS - seuils réduits 30% (plus exigeants)
            ('sportif', 'NO2', 28, 140, 30, 'Évitez le sport extérieur intense'),
            ('sportif', 'PM10', 35, 56, 30, 'Privilégiez sport en intérieur'),
            ('sportif', 'PM2.5', 17, 26, 30, 'Réduisez durée et intensité'),
            ('sportif', 'O3', 126, 168, 30, 'Sport tôt le matin uniquement'),
            ('sportif', 'SO2', 87, 262, 30, 'Évitez zones industrielles'),
            
            # PERSONNES SENSIBLES - seuils réduits 50% (très exigeants)
            ('sensible', 'NO2', 20, 100, 50, 'Restez en intérieur, fermez fenêtres'),
            ('sensible', 'PM10', 25, 40, 50, 'Portez un masque si sortie nécessaire'),
            ('sensible', 'PM2.5', 12, 17, 50, 'Évitez toute activité extérieure'),
            ('sensible', 'O3', 90, 120, 50, 'Gardez médicaments à portée'),
            ('sensible', 'SO2', 62, 175, 50, 'Consultez votre médecin si symptômes'),
            
            # PARENTS/ENFANTS - seuils réduits 40%
            ('parent', 'NO2', 24, 120, 40, 'Activités intérieures pour enfants'),
            ('parent', 'PM10', 30, 48, 40, 'Évitez parcs et aires de jeux'),
            ('parent', 'PM2.5', 15, 21, 40, 'Fermez fenêtres chambre enfants'),
            ('parent', 'O3', 108, 144, 40, 'Reportez sorties scolaires'),
            ('parent', 'SO2', 75, 210, 40, 'Surveillez signes irritation'),
            
            # SENIORS - seuils réduits 35%
            ('senior', 'NO2', 26, 130, 35, 'Reportez courses et sorties'),
            ('senior', 'PM10', 32, 52, 35, 'Consultez médecin si essoufflement'),
            ('senior', 'PM2.5', 16, 23, 35, 'Restez en intérieur climatisé'),
            ('senior', 'O3', 117, 156, 35, 'Évitez efforts physiques'),
            ('senior', 'SO2', 81, 227, 35, 'Contactez médecin si symptômes')
        ]
        
        for profil, polluant, seuil_info, seuil_alerte, reduction, conseil in seuils_data:
            cursor.execute("""
                INSERT INTO seuils_personnalises 
                (profil_type, polluant, seuil_info, seuil_alerte, pourcentage_reduction, conseil_depassement)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (profil_type, polluant) DO NOTHING
            """, (profil, polluant, seuil_info, seuil_alerte, reduction, conseil))
        
        print(f"✅ {len(seuils_data)} seuils personnalisés insérés")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erreur insertion seuils : {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def populate_recommandations_base():
    """Remplit la table recommandations_base avec les conseils pré-définis"""
    
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST'),
        database=os.getenv('PG_DATABASE'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        port=os.getenv('PG_PORT')
    )
    cursor = conn.cursor()
    
    try:
        print("💬 Insertion des recommandations de base...")
        
        recommandations = [
            # SPORTIFS
            ('sportif', 'bon', 'sport_exterieur', '✅ Conditions idéales pour le sport ! Profitez-en pleinement.', 1, 'success'),
            ('sportif', 'moyen', 'sport_exterieur', '⚠️ Réduisez intensité ou durée d\'exercice. Hydratez-vous bien.', 2, 'warning'),
            ('sportif', 'degrade', 'sport_exterieur', '🏠 Sport en intérieur recommandé ou activité légère uniquement.', 3, 'warning'),
            ('sportif', 'mauvais', 'sport_exterieur', '🚫 Évitez tout sport extérieur. Salle de sport ou repos.', 4, 'danger'),
            ('sportif', 'tres_mauvais', 'sport_exterieur', '⛔ AUCUN sport extérieur. Restez en intérieur.', 5, 'danger'),
            
            # PERSONNES SENSIBLES
            ('sensible', 'bon', 'sortie_generale', '✅ Air de qualité, sorties possibles sans restriction.', 1, 'success'),
            ('sensible', 'moyen', 'sortie_generale', '⚠️ Limitez sorties. Gardez médicaments à portée.', 2, 'warning'),
            ('sensible', 'degrade', 'sortie_generale', '🏠 Restez en intérieur. Fermez fenêtres.', 4, 'warning'),
            ('sensible', 'mauvais', 'sortie_generale', '🚨 Évitez absolument de sortir. Consultez médecin si symptômes.', 4, 'danger'),
            ('sensible', 'tres_mauvais', 'sortie_generale', '⛔ CONFINEMENT. Appelez médecin si difficultés respiratoires.', 5, 'danger'),
            
            # PARENTS
            ('parent', 'bon', 'sortie_enfant', '✅ Parfait pour activités extérieures avec enfants.', 1, 'success'),
            ('parent', 'moyen', 'sortie_enfant', '⚠️ Sortie courte OK. Évitez sport intensif enfants.', 2, 'warning'),
            ('parent', 'degrade', 'sortie_enfant', '🏠 Activités intérieures privilégiées. Fermez fenêtres.', 3, 'warning'),
            ('parent', 'mauvais', 'sortie_enfant', '🚫 Gardez enfants en intérieur. Pas de sortie école.', 4, 'danger'),
            ('parent', 'tres_mauvais', 'sortie_enfant', '⛔ Confinement enfants obligatoire. Surveillance symptômes.', 5, 'danger'),
            
            # SENIORS
            ('senior', 'bon', 'sortie_senior', '✅ Idéal pour courses et sorties santé.', 1, 'success'),
            ('senior', 'moyen', 'sortie_senior', '⚠️ Évitez heures de pointe. Sortez tôt le matin.', 2, 'warning'),
            ('senior', 'degrade', 'sortie_senior', '🏠 Reportez sorties non essentielles. Restez au frais.', 3, 'warning'),
            ('senior', 'mauvais', 'sortie_senior', '📞 Annulez sorties. Contactez médecin si malaise.', 4, 'danger'),
            ('senior', 'tres_mauvais', 'sortie_senior', '⛔ Confinement strict. Assistance médicale si besoin.', 5, 'danger')
        ]
        
        for profil, niveau, activite, conseil, urgence, icone in recommandations:
            cursor.execute("""
                INSERT INTO recommandations_base 
                (profil_cible, niveau_pollution, type_activite, conseil, niveau_urgence, icone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (profil, niveau, activite, conseil, urgence, icone))
        
        print(f"✅ {len(recommandations)} recommandations de base insérées")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erreur insertion recommandations : {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    """Lance l'insertion de toutes les données référentielles"""
    print("🚀 Démarrage population des données référentielles...")
    
    populate_seuils_personnalises()
    populate_recommandations_base()
    
    print("\n🎉 POPULATION TERMINÉE ! Vos tables sont prêtes.")
    print("\n📊 Résumé :")
    print("   - 20 seuils personnalisés (4 profils × 5 polluants)")
    print("   - 20 recommandations de base (4 profils × 5 niveaux)")

if __name__ == "__main__":
    main()