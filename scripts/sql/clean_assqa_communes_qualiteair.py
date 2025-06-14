from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_qualite_air_optimized():
    """Créer la table qualite_air optimisée (6 colonnes seulement)"""
    
    print("🏗️ CRÉATION TABLE QUALITE_AIR OPTIMISÉE")
    print("=" * 45)
    
    with engine.connect() as conn:
        try:
            # 1. Supprimer l'ancienne table
            print("🗑️ Suppression ancienne table...")
            conn.execute(text("DROP TABLE IF EXISTS qualite_air CASCADE"))
            print("   ✅ Ancienne table supprimée")
            
            # 2. Créer la nouvelle table optimisée (6 colonnes)
            print("🌬️ Création nouvelle structure optimisée...")
            
            conn.execute(text("""
                CREATE TABLE qualite_air (
                    id SERIAL PRIMARY KEY,
                    code_insee VARCHAR(10) NOT NULL,
                    code_polluant VARCHAR(10) NOT NULL,
                    valeur DECIMAL(10,3),
                    qualite_globale VARCHAR(50),
                    station_nom VARCHAR(255),
                    
                    -- Clés étrangères
                    FOREIGN KEY (code_insee) REFERENCES communes(code_insee),
                    FOREIGN KEY (code_polluant) REFERENCES polluants(code_polluant),
                    FOREIGN KEY (qualite_globale) REFERENCES indice(niveau),
                    
                    -- Contraintes
                    CONSTRAINT valeur_positive CHECK (valeur >= 0)
                )
            """))
            
            print("   ✅ Structure optimisée créée (6 colonnes)")
            print("      • id (clé primaire)")
            print("      • code_insee (commune)")
            print("      • code_polluant (polluant)")
            print("      • valeur (concentration)")
            print("      • qualite_globale (niveau)")
            print("      • station_nom (source)")
            
            # 3. Insérer des données d'exemple optimisées
            print("📊 Insertion de mesures optimisées...")
            
            mesures_data = [
                # Fort-de-France - Martinique
                ('97209', 'NO2', 32.5, 'Moyen', 'Station Fort-de-France Centre'),
                ('97209', 'PM10', 22.1, 'Bon', 'Station Fort-de-France Centre'),
                ('97209', 'O3', 95.3, 'Bon', 'Station Fort-de-France Centre'),
                
                # Caen - Normandie
                ('14118', 'NO2', 45.7, 'Dégradé', 'Station Caen Chemin Vert'),
                ('14118', 'PM10', 35.8, 'Moyen', 'Station Caen Chemin Vert'),
                ('14118', 'PM2.5', 18.2, 'Bon', 'Station Caen Chemin Vert'),
                
                # Chartres - Eure-et-Loir
                ('28085', 'NO2', 28.9, 'Bon', 'Station Chartres Fulbert'),
                ('28085', 'PM10', 31.2, 'Moyen', 'Station Chartres Fulbert'),
                ('28085', 'O3', 110.5, 'Moyen', 'Station Chartres Fulbert'),
                
                # Le Lamentin - Martinique
                ('97218', 'NO2', 26.3, 'Bon', 'Station Lamentin Aéroport'),
                ('97218', 'PM10', 28.7, 'Bon', 'Station Lamentin Aéroport'),
                
                # Rouen - Normandie
                ('76540', 'NO2', 52.1, 'Dégradé', 'Station Rouen Centre'),
                ('76540', 'PM10', 42.3, 'Moyen', 'Station Rouen Centre'),
                ('76540', 'SO2', 15.8, 'Bon', 'Station Rouen Centre'),
                
                # Dreux - Eure-et-Loir
                ('28134', 'NO2', 33.7, 'Moyen', 'Station Dreux Mendès France'),
                ('28134', 'PM10', 25.9, 'Bon', 'Station Dreux Mendès France'),
                ('28134', 'PM2.5', 15.3, 'Bon', 'Station Dreux Mendès France')
            ]
            
            for code_insee, polluant, valeur, qualite, station in mesures_data:
                conn.execute(text("""
                    INSERT INTO qualite_air (
                        code_insee, code_polluant, valeur, qualite_globale, station_nom
                    ) VALUES (
                        :code_insee, :polluant, :valeur, :qualite, :station
                    )
                """), {
                    "code_insee": code_insee, "polluant": polluant, 
                    "valeur": valeur, "qualite": qualite, "station": station
                })
            
            # 4. COMMIT
            conn.commit()
            print(f"   ✅ COMMIT effectué")
            
            # 5. Créer des index de performance
            print("🔍 Création des index optimisés...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_qualite_insee ON qualite_air(code_insee)",
                "CREATE INDEX IF NOT EXISTS idx_qualite_polluant ON qualite_air(code_polluant)",
                "CREATE INDEX IF NOT EXISTS idx_qualite_niveau ON qualite_air(qualite_globale)",
                "CREATE INDEX IF NOT EXISTS idx_qualite_composite ON qualite_air(code_insee, code_polluant)"
            ]
            
            for idx_query in index_queries:
                conn.execute(text(idx_query))
            
            conn.commit()
            print(f"   ✅ {len(index_queries)} index créés")
            
            # 6. Vérifications et statistiques
            count = conn.execute(text("SELECT COUNT(*) FROM qualite_air")).fetchone()[0]
            print(f"   📊 {count} mesures créées")
            
            # 7. Statistiques par polluant
            print(f"\n📊 STATISTIQUES PAR POLLUANT:")
            stats = conn.execute(text("""
                SELECT 
                    code_polluant,
                    COUNT(*) as nb_mesures,
                    ROUND(AVG(valeur), 2) as valeur_moyenne,
                    MIN(valeur) as val_min,
                    MAX(valeur) as val_max
                FROM qualite_air
                GROUP BY code_polluant
                ORDER BY nb_mesures DESC
            """)).fetchall()
            
            for polluant, nb_mesures, val_moy, val_min, val_max in stats:
                print(f"   • {polluant}: {nb_mesures} mesures (moy: {val_moy}, min: {val_min}, max: {val_max})")
            
            # 8. Statistiques par commune
            print(f"\n🏘️ STATISTIQUES PAR COMMUNE:")
            communes_stats = conn.execute(text("""
                SELECT 
                    c.nom_commune,
                    a.nom_region,
                    COUNT(q.id) as nb_mesures,
                    COUNT(DISTINCT q.code_polluant) as nb_polluants,
                    ROUND(AVG(q.valeur), 2) as valeur_moyenne
                FROM qualite_air q
                JOIN communes c ON q.code_insee = c.code_insee
                JOIN aasqa_regions a ON c.aasqa_code = a.aasqa_code
                GROUP BY c.nom_commune, a.nom_region
                ORDER BY nb_mesures DESC
            """)).fetchall()
            
            for commune, region, nb_mesures, nb_polluants, val_moy in communes_stats:
                print(f"   • {commune} ({region}): {nb_mesures} mesures, {nb_polluants} polluants (moy: {val_moy})")
            
            # 9. Statistiques par niveau de qualité
            print(f"\n🎨 STATISTIQUES PAR NIVEAU DE QUALITÉ:")
            qualite_stats = conn.execute(text("""
                SELECT 
                    i.niveau,
                    i.couleur,
                    COUNT(q.id) as nb_mesures,
                    ROUND(AVG(q.valeur), 2) as valeur_moyenne
                FROM qualite_air q
                JOIN indice i ON q.qualite_globale = i.niveau
                GROUP BY i.niveau, i.couleur
                ORDER BY valeur_moyenne
            """)).fetchall()
            
            for niveau, couleur, nb_mesures, val_moy in qualite_stats:
                print(f"   • {niveau} ({couleur}): {nb_mesures} mesures (moy: {val_moy} µg/m³)")
            
            # 10. Test de jointure complète
            print(f"\n🔗 TEST DE JOINTURES COMPLÈTES:")
            test_join = conn.execute(text("""
                SELECT 
                    a.nom_region,
                    c.nom_commune,
                    q.code_polluant,
                    p.unite_mesure,
                    q.valeur,
                    q.qualite_globale,
                    i.couleur,
                    q.station_nom
                FROM qualite_air q
                JOIN communes c ON q.code_insee = c.code_insee
                JOIN aasqa_regions a ON c.aasqa_code = a.aasqa_code
                JOIN polluants p ON q.code_polluant = p.code_polluant
                JOIN indice i ON q.qualite_globale = i.niveau
                ORDER BY q.valeur DESC
                LIMIT 3
            """)).fetchall()
            
            print("   📋 Top 3 des valeurs les plus élevées:")
            for region, commune, polluant, unite, valeur, qualite, couleur, station in test_join:
                print(f"      {region} > {commune} > {station}")
                print(f"         {polluant}: {valeur} {unite} → {qualite} ({couleur})")
            
            print(f"\n🎉 TABLE QUALITE_AIR OPTIMISÉE CRÉÉE AVEC SUCCÈS !")
            print("✅ Structure allégée (6 colonnes seulement)")
            print("✅ Pas de colonnes temporelles redondantes")
            print("✅ Relations fonctionnelles avec toutes les tables")
            print("✅ Index optimisés pour les performances")
            print("✅ Données d'exemple pour vos analyses")
            print("✅ Capacité d'analyse quantitative ET qualitative")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    create_qualite_air_optimized()