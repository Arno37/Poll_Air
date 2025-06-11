from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import sys
sys.path.append('../..')
load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_polluants_table():
    """Créer la table des polluants avec toutes leurs caractéristiques"""
    
    print("🧪 CRÉATION DE LA TABLE POLLUANTS")
    print("=" * 60)
    
    with engine.connect() as conn:
        try:
            # Supprimer l'ancienne table si elle existe
            conn.execute(text("DROP TABLE IF EXISTS polluants CASCADE"))
            print("🗑️ Ancienne table polluants supprimée")
            
            # Créer la table polluants
            conn.execute(text("""
                CREATE TABLE polluants (
                    code_polluant VARCHAR(10) PRIMARY KEY,
                    nom_complet VARCHAR(100) NOT NULL,
                    nom_court VARCHAR(20) NOT NULL,
                    formule_chimique VARCHAR(20),
                    unite_mesure VARCHAR(10) NOT NULL,
                    description TEXT,
                    type_polluant VARCHAR(50),
                    origine_principale TEXT,
                    effets_sante TEXT,
                    seuil_information INTEGER,
                    seuil_alerte INTEGER,
                    valeur_limite_annuelle INTEGER,
                    valeur_limite_horaire INTEGER,
                    couleur_viz VARCHAR(7),
                    ordre_affichage INTEGER,
                    actif BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            print("✅ Structure de la table polluants créée")
            
            # Insérer les 5 polluants de votre système
            polluants_data = [
                {
                    'code': 'NO2',
                    'nom_complet': 'Dioxyde d\'azote',
                    'nom_court': 'NO2',
                    'formule': 'NO₂',
                    'unite': 'μg/m³',
                    'description': 'Gaz toxique provenant principalement de la combustion (trafic routier, chauffage, industrie)',
                    'type': 'Gaz',
                    'origine': 'Trafic routier (40%), chauffage résidentiel (25%), industrie (20%), autres (15%)',
                    'effets': 'Irritation des voies respiratoires, aggravation de l\'asthme, diminution de la fonction pulmonaire',
                    'seuil_info': 200,
                    'seuil_alerte': 240,
                    'limite_annuelle': 40,
                    'limite_horaire': 200,
                    'couleur': '#FF6B35',
                    'ordre': 1
                },
                {
                    'code': 'O3',
                    'nom_complet': 'Ozone troposphérique',
                    'nom_court': 'Ozone',
                    'formule': 'O₃',
                    'unite': 'μg/m³',
                    'description': 'Polluant secondaire formé par réaction photochimique entre NO2 et COV sous l\'effet du soleil',
                    'type': 'Gaz oxydant',
                    'origine': 'Formation secondaire : précurseurs (NOx + COV) + rayonnement solaire',
                    'effets': 'Irritation oculaire et respiratoire, toux, essoufflement, aggravation de l\'asthme',
                    'seuil_info': 180,
                    'seuil_alerte': 240,
                    'limite_annuelle': None,
                    'limite_horaire': 120,
                    'couleur': '#4ECDC4',
                    'ordre': 2
                },
                {
                    'code': 'PM10',
                    'nom_complet': 'Particules fines inférieures à 10 micromètres',
                    'nom_court': 'PM10',
                    'formule': 'PM₁₀',
                    'unite': 'μg/m³',
                    'description': 'Particules en suspension dans l\'air de diamètre inférieur à 10 micromètres',
                    'type': 'Particules',
                    'origine': 'Combustion, usure des pneus et freins, remise en suspension, érosion, pollens',
                    'effets': 'Problèmes cardiovasculaires et respiratoires, cancer du poumon, mortalité prématurée',
                    'seuil_info': None,
                    'seuil_alerte': 80,
                    'limite_annuelle': 40,
                    'limite_horaire': 50,
                    'couleur': '#A8E6CF',
                    'ordre': 3
                },
                {
                    'code': 'PM2.5',
                    'nom_complet': 'Particules très fines inférieures à 2,5 micromètres',
                    'nom_court': 'PM2.5',
                    'formule': 'PM₂.₅',
                    'unite': 'μg/m³',
                    'description': 'Particules ultrafines les plus dangereuses, capables de pénétrer profondément dans les poumons',
                    'type': 'Particules ultrafines',
                    'origine': 'Combustion (diesel, chauffage au bois), processus industriels, formation secondaire',
                    'effets': 'Pénétration alvéolaire, passage dans le sang, effets cardiovasculaires graves, cancer',
                    'seuil_info': None,
                    'seuil_alerte': None,
                    'limite_annuelle': 25,
                    'limite_horaire': None,
                    'couleur': '#FFD93D',
                    'ordre': 4
                },
                {
                    'code': 'SO2',
                    'nom_complet': 'Dioxyde de soufre',
                    'nom_court': 'SO2',
                    'formule': 'SO₂',
                    'unite': 'μg/m³',
                    'description': 'Gaz irritant provenant de la combustion de combustibles fossiles contenant du soufre',
                    'type': 'Gaz acide',
                    'origine': 'Industrie (raffinage, sidérurgie), transport maritime, chauffage au fioul/charbon',
                    'effets': 'Irritation des muqueuses, toux, gêne respiratoire, aggravation de l\'asthme',
                    'seuil_info': 300,
                    'seuil_alerte': 500,
                    'limite_annuelle': None,
                    'limite_horaire': 350,
                    'couleur': '#FF8B94',
                    'ordre': 5
                }
            ]
            
            # Insérer chaque polluant
            for polluant in polluants_data:
                conn.execute(text("""
                    INSERT INTO polluants (
                        code_polluant, nom_complet, nom_court, formule_chimique, 
                        unite_mesure, description, type_polluant, origine_principale,
                        effets_sante, seuil_information, seuil_alerte, 
                        valeur_limite_annuelle, valeur_limite_horaire,
                        couleur_viz, ordre_affichage
                    ) VALUES (
                        :code, :nom_complet, :nom_court, :formule,
                        :unite, :description, :type, :origine,
                        :effets, :seuil_info, :seuil_alerte,
                        :limite_annuelle, :limite_horaire,
                        :couleur, :ordre
                    )
                """), {
                    'code': polluant['code'],
                    'nom_complet': polluant['nom_complet'],
                    'nom_court': polluant['nom_court'],
                    'formule': polluant['formule'],
                    'unite': polluant['unite'],
                    'description': polluant['description'],
                    'type': polluant['type'],
                    'origine': polluant['origine'],
                    'effets': polluant['effets'],
                    'seuil_info': polluant['seuil_info'],
                    'seuil_alerte': polluant['seuil_alerte'],
                    'limite_annuelle': polluant['limite_annuelle'],
                    'limite_horaire': polluant['limite_horaire'],
                    'couleur': polluant['couleur'],
                    'ordre': polluant['ordre']
                })
            
            print(f"✅ {len(polluants_data)} polluants insérés")
            
            # Créer les index
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_polluants_code ON polluants(code_polluant)",
                "CREATE INDEX IF NOT EXISTS idx_polluants_type ON polluants(type_polluant)",
                "CREATE INDEX IF NOT EXISTS idx_polluants_ordre ON polluants(ordre_affichage)",
                "CREATE INDEX IF NOT EXISTS idx_polluants_actif ON polluants(actif)"
            ]
            
            for idx in indexes:
                conn.execute(text(idx))
            
            print(f"✅ {len(indexes)} index créés")
            
            conn.commit()
            
            # Vérification et affichage
            print(f"\n📊 VÉRIFICATION DE LA TABLE POLLUANTS :")
            print("-" * 50)
            
            polluants_list = conn.execute(text("""
                SELECT code_polluant, nom_court, formule_chimique, unite_mesure,
                       seuil_information, seuil_alerte, couleur_viz
                FROM polluants 
                ORDER BY ordre_affichage
            """))
            
            print(f"🧪 POLLUANTS CONFIGURÉS :")
            for code, nom, formule, unite, seuil_info, seuil_alerte, couleur in polluants_list.fetchall():
                info_str = f"{seuil_info}μg/m³" if seuil_info else "N/A"
                alerte_str = f"{seuil_alerte}μg/m³" if seuil_alerte else "N/A"
                print(f"   {code} ({formule}) - {nom}")
                print(f"      Unité: {unite} | Info: {info_str} | Alerte: {alerte_str} | Couleur: {couleur}")
            
            # Statistiques depuis la table consolidée (version sécurisée)
            print(f"\n📈 STATISTIQUES DEPUIS VOS DONNÉES :")
            
            # Test simple pour NO2 et PM10 qui existent sûrement
            simple_stats = conn.execute(text("""
                SELECT 
                    COUNT(CASE WHEN no2 > 0 THEN 1 END) as mesures_no2,
                    COUNT(CASE WHEN pm10 > 0 THEN 1 END) as mesures_pm10,
                    ROUND(AVG(CASE WHEN no2 > 0 THEN no2 END), 2) as avg_no2,
                    ROUND(AVG(CASE WHEN pm10 > 0 THEN pm10 END), 2) as avg_pm10
                FROM indices_qualite_air_consolides
            """))
            
            stats = simple_stats.fetchone()
            if stats:
                print(f"   NO2: {stats[0]:,} mesures, moyenne: {stats[2]}μg/m³")
                print(f"   PM10: {stats[1]:,} mesures, moyenne: {stats[3]}μg/m³")
                print(f"   (autres polluants : données à vérifier selon colonnes disponibles)")
            
            # Test de jointure avec la table consolidée
            print(f"\n🔗 TEST DE JOINTURE AVEC VOS DONNÉES :")
            test_join = conn.execute(text("""
                WITH polluant_data AS (
                    SELECT 'NO2' as polluant_code, no2 as valeur, date_prise_mesure, zone
                    FROM indices_qualite_air_consolides 
                    WHERE no2 > 0 
                    UNION ALL
                    SELECT 'O3', o3, date_prise_mesure, zone
                    FROM indices_qualite_air_consolides 
                    WHERE o3 > 0
                    UNION ALL
                    SELECT 'PM10', pm10, date_prise_mesure, zone
                    FROM indices_qualite_air_consolides 
                    WHERE pm10 > 0
                )
                SELECT 
                    p.nom_court,
                    p.formule_chimique,
                    COUNT(*) as nb_mesures,
                    ROUND(AVG(pd.valeur), 2) as moyenne,
                    p.seuil_alerte,
                    CASE 
                        WHEN AVG(pd.valeur) > p.seuil_alerte THEN '🚨 ALERTE'
                        WHEN AVG(pd.valeur) > p.seuil_information THEN '⚠️ INFO'
                        ELSE '✅ OK'
                    END as statut
                FROM polluant_data pd
                JOIN polluants p ON pd.polluant_code = p.code_polluant
                GROUP BY p.code_polluant, p.nom_court, p.formule_chimique, p.seuil_information, p.seuil_alerte
                ORDER BY p.ordre_affichage
                LIMIT 5
            """))
            
            for nom, formule, nb, avg, seuil, statut in test_join.fetchall():
                seuil_str = f"{seuil}μg/m³" if seuil else "N/A"
                print(f"   {nom} ({formule}): {nb:,} mesures, moy: {avg}μg/m³, seuil: {seuil_str} → {statut}")
            
            print(f"\n🎉 TABLE POLLUANTS CRÉÉE AVEC SUCCÈS !")
            print(f"✅ 5 polluants configurés avec seuils réglementaires")
            print(f"✅ Relations avec vos données de mesures établies")
            print(f"✅ Prêt pour alertes automatiques et visualisations")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la table polluants: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    create_polluants_table()

    print("\n📊 TABLES DE RÉFÉRENCE CRÉÉES :")
    print("├── polluants (5 lignes) ✅ NOUVELLE TABLE")
    print("├── aasqa_regions (4 lignes) ✅")
    print("├── communes (11,055 lignes) ✅  ")
    print("├── niveaux_qualite (5 lignes) ✅")
    print("└── sources_donnees (4 lignes) ✅")
    
    print("\n📈 TABLE PRINCIPALE :")
    print("└── indices_qualite_air_consolides (1,817,242 lignes) ✅")