from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

def create_qualite_air_pm25():
    """Créer la table qualite_air avec PM2.5 (pas PM25)"""
    
    print("🏗️ CRÉATION TABLE QUALITE_AIR (PM2.5 CORRIGÉ)")
    print("=" * 48)
    
    with engine.connect() as conn:
        try:
            # 1. Créer la table
            print("🌬️ Création table 'qualite_air'...")
            
            conn.execute(text("DROP TABLE IF EXISTS qualite_air CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE qualite_air (
                    id SERIAL PRIMARY KEY,
                    code_insee VARCHAR(10) NOT NULL,
                    code_polluant VARCHAR(10) NOT NULL,
                    date_mesure DATE NOT NULL,
                    heure_mesure TIME,
                    valeur DECIMAL(10,3),
                    unite VARCHAR(20),
                    qualite_globale VARCHAR(50),
                    station_nom VARCHAR(255),
                    source_donnee VARCHAR(100),
                    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Clés étrangères
                    FOREIGN KEY (code_insee) REFERENCES communes(code_insee),
                    FOREIGN KEY (code_polluant) REFERENCES polluants(code_polluant),
                    FOREIGN KEY (qualite_globale) REFERENCES indice(niveau),
                    
                    -- Contraintes
                    CONSTRAINT valeur_positive CHECK (valeur >= 0)
                )
            """))
            
            print("   ✅ Structure créée")
            
            # 2. Insérer des mesures avec PM2.5 (pas PM25)
            print("📊 Insertion de mesures avec PM2.5...")
            
            mesures_data = [
                # Fort-de-France - Martinique
                ('97209', 'NO2', '2024-06-14', '10:00:00', 32.5, 'µg/m³', 'Moyen', 'Station Fort-de-France Centre'),
                ('97209', 'PM10', '2024-06-14', '10:00:00', 22.1, 'µg/m³', 'Bon', 'Station Fort-de-France Centre'),
                ('97209', 'O3', '2024-06-14', '10:00:00', 95.3, 'µg/m³', 'Bon', 'Station Fort-de-France Centre'),
                
                # Caen - Normandie (avec PM2.5 corrigé)
                ('14118', 'NO2', '2024-06-14', '10:00:00', 45.7, 'µg/m³', 'Dégradé', 'Station Caen Chemin Vert'),
                ('14118', 'PM10', '2024-06-14', '10:00:00', 35.8, 'µg/m³', 'Moyen', 'Station Caen Chemin Vert'),
                ('14118', 'PM2.5', '2024-06-14', '10:00:00', 18.2, 'µg/m³', 'Bon', 'Station Caen Chemin Vert'),
                
                # Chartres - Eure-et-Loir
                ('28085', 'NO2', '2024-06-14', '10:00:00', 28.9, 'µg/m³', 'Bon', 'Station Chartres Fulbert'),
                ('28085', 'PM10', '2024-06-14', '10:00:00', 31.2, 'µg/m³', 'Moyen', 'Station Chartres Fulbert'),
                ('28085', 'O3', '2024-06-14', '10:00:00', 110.5, 'µg/m³', 'Moyen', 'Station Chartres Fulbert'),
                
                # Le Lamentin - Martinique
                ('97218', 'NO2', '2024-06-14', '11:00:00', 26.3, 'µg/m³', 'Bon', 'Station Lamentin Aéroport'),
                ('97218', 'PM10', '2024-06-14', '11:00:00', 28.7, 'µg/m³', 'Bon', 'Station Lamentin Aéroport'),
                
                # Rouen - Normandie
                ('76540', 'NO2', '2024-06-14', '11:00:00', 52.1, 'µg/m³', 'Dégradé', 'Station Rouen Centre'),
                ('76540', 'PM10', '2024-06-14', '11:00:00', 42.3, 'µg/m³', 'Moyen', 'Station Rouen Centre'),
                ('76540', 'SO2', '2024-06-14', '11:00:00', 15.8, 'µg/m³', 'Bon', 'Station Rouen Centre'),
                
                # Dreux - Eure-et-Loir avec PM2.5
                ('28134', 'NO2', '2024-06-14', '12:00:00', 33.7, 'µg/m³', 'Moyen', 'Station Dreux Mendès France'),
                ('28134', 'PM10', '2024-06-14', '12:00:00', 25.9, 'µg/m³', 'Bon', 'Station Dreux Mendès France'),
                ('28134', 'PM2.5', '2024-06-14', '12:00:00', 15.3, 'µg/m³', 'Bon', 'Station Dreux Mendès France')
            ]
            
            for code_insee, polluant, date, heure, valeur, unite, qualite, station in mesures_data:
                conn.execute(text("""
                    INSERT INTO qualite_air (
                        code_insee, code_polluant, date_mesure, heure_mesure,
                        valeur, unite, qualite_globale, station_nom, source_donnee
                    ) VALUES (
                        :code_insee, :polluant, :date, :heure,
                        :valeur, :unite, :qualite, :station, 'EXEMPLE_PM2.5'
                    )
                """), {
                    "code_insee": code_insee, "polluant": polluant, "date": date, "heure": heure,
                    "valeur": valeur, "unite": unite, "qualite": qualite, "station": station
                })
            
            # 3. COMMIT
            conn.commit()
            print(f"   ✅ COMMIT effectué")
            
            # 4. Vérification
            count = conn.execute(text("SELECT COUNT(*) FROM qualite_air")).fetchone()[0]
            print(f"   📊 {count} mesures créées")
            
            # 5. Statistiques par polluant
            print(f"\n📊 RÉPARTITION PAR POLLUANT:")
            stats = conn.execute(text("""
                SELECT 
                    q.code_polluant,
                    p.nom_polluant,
                    COUNT(q.id) as nb_mesures,
                    ROUND(AVG(q.valeur), 2) as valeur_moyenne
                FROM qualite_air q
                JOIN polluants p ON q.code_polluant = p.code_polluant
                GROUP BY q.code_polluant, p.nom_polluant
                ORDER BY nb_mesures DESC
            """)).fetchall()
            
            for code, nom, nb_mesures, val_moy in stats:
                print(f"   • {code} ({nom}): {nb_mesures} mesures (moy: {val_moy} µg/m³)")
            
            print(f"\n🎉 TABLE QUALITE_AIR CRÉÉE AVEC PM2.5 CORRECT !")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    create_qualite_air_pm25()