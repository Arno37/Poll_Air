"""
Script hybride de récupération de données PostgreSQL et MongoDB.

Ce script permet de récupérer et croiser des données depuis les deux bases :
- PostgreSQL : données consolidées de qualité de l'air
- MongoDB : épisodes de pollution et moyennes journalières géolocalisées

Functions:
    get_pg_data: Récupère les données PostgreSQL
    get_mongo_data: Récupère les données MongoDB
    cross_reference_data: Croise les données des deux sources
    export_combined_data: Exporte les résultats combinés

Usage:
    python hybrid_data_retrieval.py --zone 972 --date-debut 2024-11-01 --format json
"""

import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import pandas as pd
import json
from datetime import datetime, timedelta
import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import du système de logging existant
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
from logger import log_api_call, logger

@dataclass
class DataRetrievalConfig:
    """Configuration pour la récupération de données"""
    # PostgreSQL
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_database: str = "qualite_air"
    pg_user: str = "postgres"
    pg_password: str = ""
    
    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_database: str = "pollution_data"
    
    # Filtres
    zone_filter: Optional[str] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    polluants: List[str] = None
    
    # Export
    output_format: str = "json"  # json, csv, excel
    output_file: Optional[str] = None

class HybridDataRetriever:
    """Classe principale pour la récupération hybride de données"""
    
    def __init__(self, config: DataRetrievalConfig):
        self.config = config
        self.pg_conn = None
        self.mongo_client = None
        self.mongo_db = None
        
    def __enter__(self):
        """Gestionnaire de contexte pour les connexions"""
        self.connect_databases()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fermeture des connexions"""
        self.close_connections()
        
    def connect_databases(self):
        """Établit les connexions aux bases de données"""
        try:
            # Connexion PostgreSQL
            self.pg_conn = psycopg2.connect(
                host=self.config.pg_host,
                port=self.config.pg_port,
                database=self.config.pg_database,
                user=self.config.pg_user,
                password=self.config.pg_password
            )
            logger.info("Connexion PostgreSQL établie")
            
            # Connexion MongoDB
            self.mongo_client = MongoClient(self.config.mongo_uri)
            self.mongo_db = self.mongo_client[self.config.mongo_database]
            logger.info("Connexion MongoDB établie")
            
        except Exception as e:
            logger.error(f"Erreur connexion bases de données: {e}")
            raise
            
    def close_connections(self):
        """Ferme les connexions aux bases de données"""
        if self.pg_conn:
            self.pg_conn.close()
            logger.info("Connexion PostgreSQL fermée")
            
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("Connexion MongoDB fermée")
    
    def get_pg_data(self) -> List[Dict]:
        """
        Récupère les données PostgreSQL avec filtres
        
        Returns:
            List[Dict]: Liste des mesures de qualité de l'air
        """
        try:
            cursor = self.pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Construction de la requête dynamique
            query = """
            SELECT 
                id,
                aasqa,
                no2,
                o3,
                pm10,
                pm25,
                date_prise_mesure,
                qualite_air,
                zone,
                code_zone,
                fichier_source,
                created_at
            FROM indices_qualite_air_consolides
            WHERE 1=1
            """
            params = []
            
            # Filtres dynamiques
            if self.config.zone_filter:
                if len(self.config.zone_filter) <= 3:
                    query += " AND code_zone LIKE %s"
                    params.append(f"{self.config.zone_filter}%")
                else:
                    query += " AND code_zone = %s"
                    params.append(self.config.zone_filter)
            
            if self.config.date_debut:
                query += " AND date_prise_mesure >= %s"
                params.append(self.config.date_debut)
                
            if self.config.date_fin:
                query += " AND date_prise_mesure <= %s"
                params.append(self.config.date_fin)
            
            # Ordre et limite
            query += " ORDER BY date_prise_mesure DESC LIMIT 10000"
            
            # Exécution
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Conversion en liste de dictionnaires
            pg_data = [dict(row) for row in results]
            
            logger.info(f"PostgreSQL: {len(pg_data)} enregistrements récupérés")
            log_api_call("postgresql_query", "system", {
                "zone": self.config.zone_filter,
                "date_debut": self.config.date_debut,
                "records": len(pg_data)
            })
            
            return pg_data
            
        except Exception as e:
            logger.error(f"Erreur récupération PostgreSQL: {e}")
            raise
    
    def get_mongo_episodes(self) -> List[Dict]:
        """
        Récupère les épisodes de pollution depuis MongoDB
        
        Returns:
            List[Dict]: Liste des épisodes de pollution
        """
        try:
            collection = self.mongo_db['EPIS_POLLUTION']
            
            # Construction du filtre MongoDB
            mongo_filter = {}
            
            if self.config.zone_filter:
                mongo_filter["properties.code_insee"] = {"$regex": f"^{self.config.zone_filter}"}
            
            if self.config.date_debut:
                mongo_filter["properties.date_debut"] = {"$gte": self.config.date_debut}
            
            if self.config.polluants:
                mongo_filter["properties.polluant"] = {"$in": self.config.polluants}
            
            # Projection pour optimiser
            projection = {
                "properties.code_insee": 1,
                "properties.polluant": 1,
                "properties.date_debut": 1,
                "properties.date_fin": 1,
                "properties.etat": 1,
                "properties.niveau": 1,
                "properties.valeur_declenchement": 1,
                "geometry.coordinates": 1
            }
            
            # Exécution de la requête
            cursor = collection.find(mongo_filter, projection).limit(5000)
            episodes = list(cursor)
            
            # Aplatissement des données
            flattened_episodes = []
            for episode in episodes:
                props = episode.get('properties', {})
                geom = episode.get('geometry', {})
                coords = geom.get('coordinates', [None, None])
                
                flattened_episodes.append({
                    'episode_id': str(episode['_id']),
                    'code_insee': props.get('code_insee'),
                    'polluant': props.get('polluant'),
                    'date_debut': props.get('date_debut'),
                    'date_fin': props.get('date_fin'),
                    'etat': props.get('etat'),
                    'niveau': props.get('niveau'),
                    'valeur_declenchement': props.get('valeur_declenchement'),
                    'longitude': coords[0],
                    'latitude': coords[1]
                })
            
            logger.info(f"MongoDB Episodes: {len(flattened_episodes)} enregistrements récupérés")
            log_api_call("mongodb_episodes_query", "system", {
                "zone": self.config.zone_filter,
                "records": len(flattened_episodes)
            })
            
            return flattened_episodes
            
        except Exception as e:
            logger.error(f"Erreur récupération MongoDB episodes: {e}")
            raise
    
    def get_mongo_moyennes(self) -> List[Dict]:
        """
        Récupère les moyennes journalières depuis MongoDB
        
        Returns:
            List[Dict]: Liste des moyennes journalières
        """
        try:
            collection = self.mongo_db['MOY_JOURNALIERE']
            
            # Construction du filtre
            mongo_filter = {}
            
            if self.config.date_debut:
                mongo_filter["date_debut"] = {"$gte": self.config.date_debut}
            
            if self.config.polluants:
                mongo_filter["polluant"] = {"$in": self.config.polluants}
            
            # Projection optimisée
            projection = {
                "date_debut": 1,
                "organisme": 1,
                "nom_site": 1,
                "polluant": 1,
                "valeur": 1,
                "unite_mesure": 1,
                "coordinates": 1,
                "code_site": 1
            }
            
            # Exécution
            cursor = collection.find(mongo_filter, projection).limit(5000)
            moyennes = list(cursor)
            
            # Aplatissement
            flattened_moyennes = []
            for moyenne in moyennes:
                coords = moyenne.get('coordinates', [None, None])
                
                flattened_moyennes.append({
                    'moyenne_id': str(moyenne['_id']),
                    'date_debut': moyenne.get('date_debut'),
                    'organisme': moyenne.get('organisme'),
                    'nom_site': moyenne.get('nom_site'),
                    'code_site': moyenne.get('code_site'),
                    'polluant': moyenne.get('polluant'),
                    'valeur': moyenne.get('valeur'),
                    'unite_mesure': moyenne.get('unite_mesure'),
                    'longitude': coords[0] if coords else None,
                    'latitude': coords[1] if coords else None
                })
            
            logger.info(f"MongoDB Moyennes: {len(flattened_moyennes)} enregistrements récupérés")
            log_api_call("mongodb_moyennes_query", "system", {
                "records": len(flattened_moyennes)
            })
            
            return flattened_moyennes
            
        except Exception as e:
            logger.error(f"Erreur récupération MongoDB moyennes: {e}")
            raise
    
    def cross_reference_data(self, pg_data: List[Dict], mongo_episodes: List[Dict], 
                           mongo_moyennes: List[Dict]) -> Dict:
        """
        Croise les données des différentes sources
        
        Args:
            pg_data: Données PostgreSQL
            mongo_episodes: Épisodes MongoDB
            mongo_moyennes: Moyennes MongoDB
            
        Returns:
            Dict: Données croisées avec statistiques
        """
        try:
            # Conversion en DataFrames pour faciliter les analyses
            df_pg = pd.DataFrame(pg_data)
            df_episodes = pd.DataFrame(mongo_episodes)
            df_moyennes = pd.DataFrame(mongo_moyennes)
            
            # Statistiques par source
            stats = {
                'postgresql': {
                    'count': len(df_pg),
                    'date_range': {
                        'min': df_pg['date_prise_mesure'].min() if not df_pg.empty else None,
                        'max': df_pg['date_prise_mesure'].max() if not df_pg.empty else None
                    },
                    'zones_uniques': df_pg['code_zone'].nunique() if not df_pg.empty else 0,
                    'polluants_moyens': {
                        'no2_moy': df_pg['no2'].mean() if not df_pg.empty else None,
                        'o3_moy': df_pg['o3'].mean() if not df_pg.empty else None,
                        'pm10_moy': df_pg['pm10'].mean() if not df_pg.empty else None,
                        'pm25_moy': df_pg['pm25'].mean() if not df_pg.empty else None
                    }
                },
                'mongodb_episodes': {
                    'count': len(df_episodes),
                    'etats': df_episodes['etat'].value_counts().to_dict() if not df_episodes.empty else {},
                    'polluants': df_episodes['polluant'].value_counts().to_dict() if not df_episodes.empty else {},
                    'niveaux': df_episodes['niveau'].value_counts().to_dict() if not df_episodes.empty else {}
                },
                'mongodb_moyennes': {
                    'count': len(df_moyennes),
                    'organismes': df_moyennes['organisme'].value_counts().to_dict() if not df_moyennes.empty else {},
                    'polluants': df_moyennes['polluant'].value_counts().to_dict() if not df_moyennes.empty else {},
                    'valeur_moyenne': df_moyennes['valeur'].mean() if not df_moyennes.empty else None
                }
            }
            
            # Recherche de correspondances temporelles
            correspondances = []
            if not df_pg.empty and not df_episodes.empty:
                # Jointure approximative sur la date
                for _, pg_row in df_pg.head(100).iterrows():  # Limite pour performance
                    date_pg = pd.to_datetime(pg_row['date_prise_mesure'])
                    
                    # Recherche d'épisodes dans une fenêtre de ±1 jour
                    episodes_proches = df_episodes[
                        (pd.to_datetime(df_episodes['date_debut']) >= date_pg - timedelta(days=1)) &
                        (pd.to_datetime(df_episodes['date_debut']) <= date_pg + timedelta(days=1))
                    ]
                    
                    if not episodes_proches.empty:
                        correspondances.append({
                            'pg_id': pg_row['id'],
                            'pg_zone': pg_row['code_zone'],
                            'pg_date': pg_row['date_prise_mesure'],
                            'pg_qualite': pg_row['qualite_air'],
                            'episodes_associes': len(episodes_proches),
                            'episodes_details': episodes_proches[['polluant', 'etat', 'niveau']].to_dict('records')
                        })
            
            # Résultat final
            result = {
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'zone_filter': self.config.zone_filter,
                    'date_debut': self.config.date_debut,
                    'date_fin': self.config.date_fin,
                    'polluants': self.config.polluants
                },
                'statistics': stats,
                'correspondances_temporelles': correspondances[:50],  # Limite pour taille
                'raw_data': {
                    'postgresql_sample': pg_data[:10],  # Échantillon
                    'mongodb_episodes_sample': mongo_episodes[:10],
                    'mongodb_moyennes_sample': mongo_moyennes[:10]
                }
            }
            
            logger.info(f"Croisement terminé: {len(correspondances)} correspondances trouvées")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur croisement données: {e}")
            raise
    
    def export_data(self, data: Dict, output_file: str = None):
        """
        Exporte les données dans le format demandé
        
        Args:
            data: Données à exporter
            output_file: Fichier de sortie (optionnel)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.config.output_format.lower() == 'json':
                filename = output_file or f"hybrid_data_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Données exportées en JSON: {filename}")
                
            elif self.config.output_format.lower() == 'csv':
                filename = output_file or f"hybrid_data_{timestamp}.csv"
                
                # Export des correspondances en CSV
                if data['correspondances_temporelles']:
                    df = pd.DataFrame(data['correspondances_temporelles'])
                    df.to_csv(filename, index=False, encoding='utf-8')
                    logger.info(f"Correspondances exportées en CSV: {filename}")
                
                # Export des statistiques en CSV séparé
                stats_file = f"stats_{timestamp}.csv"
                stats_df = pd.DataFrame([
                    {'source': 'PostgreSQL', 'count': data['statistics']['postgresql']['count']},
                    {'source': 'MongoDB Episodes', 'count': data['statistics']['mongodb_episodes']['count']},
                    {'source': 'MongoDB Moyennes', 'count': data['statistics']['mongodb_moyennes']['count']}
                ])
                stats_df.to_csv(stats_file, index=False)
                logger.info(f"Statistiques exportées: {stats_file}")
                
            elif self.config.output_format.lower() == 'excel':
                filename = output_file or f"hybrid_data_{timestamp}.xlsx"
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Onglet statistiques
                    stats_df = pd.DataFrame([
                        {'Source': 'PostgreSQL', 'Nombre': data['statistics']['postgresql']['count']},
                        {'Source': 'MongoDB Episodes', 'Nombre': data['statistics']['mongodb_episodes']['count']},
                        {'Source': 'MongoDB Moyennes', 'Nombre': data['statistics']['mongodb_moyennes']['count']}
                    ])
                    stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
                    
                    # Onglet correspondances
                    if data['correspondances_temporelles']:
                        corr_df = pd.DataFrame(data['correspondances_temporelles'])
                        # Supprimer les colonnes complexes pour Excel
                        corr_df = corr_df.drop(columns=['episodes_details'], errors='ignore')
                        corr_df.to_excel(writer, sheet_name='Correspondances', index=False)
                    
                    # Onglets échantillons
                    if data['raw_data']['postgresql_sample']:
                        pg_df = pd.DataFrame(data['raw_data']['postgresql_sample'])
                        pg_df.to_excel(writer, sheet_name='PostgreSQL', index=False)
                    
                    if data['raw_data']['mongodb_episodes_sample']:
                        ep_df = pd.DataFrame(data['raw_data']['mongodb_episodes_sample'])
                        ep_df.to_excel(writer, sheet_name='Episodes', index=False)
                
                logger.info(f"Données exportées en Excel: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Erreur export données: {e}")
            raise
    
    def run_hybrid_retrieval(self) -> str:
        """
        Exécute la récupération hybride complète
        
        Returns:
            str: Chemin du fichier de sortie
        """
        try:
            logger.info("Début récupération hybride de données")
            
            # Récupération des données
            pg_data = self.get_pg_data()
            mongo_episodes = self.get_mongo_episodes()
            mongo_moyennes = self.get_mongo_moyennes()
            
            # Croisement des données
            combined_data = self.cross_reference_data(pg_data, mongo_episodes, mongo_moyennes)
            
            # Export
            output_file = self.export_data(combined_data, self.config.output_file)
            
            logger.info(f"Récupération hybride terminée avec succès: {output_file}")
            log_api_call("hybrid_data_retrieval", "system", {
                "pg_records": len(pg_data),
                "mongo_episodes": len(mongo_episodes),
                "mongo_moyennes": len(mongo_moyennes),
                "output_file": output_file
            })
            
            return output_file
            
        except Exception as e:
            logger.error(f"Erreur récupération hybride: {e}")
            raise

    def get_one_sql_one_mongo(self) -> dict:
        """
        Récupère une seule donnée depuis PostgreSQL et une seule depuis MongoDB (épisode)
        Returns:
            dict: {'sql': ..., 'mongo': ...}
        """
        try:
            # Récupérer une seule donnée SQL
            pg_data = self.get_pg_data()
            one_sql = pg_data[0] if pg_data else None

            # Récupérer une seule donnée MongoDB (épisode)
            mongo_data = self.get_mongo_episodes()
            one_mongo = mongo_data[0] if mongo_data else None

            return {'sql': one_sql, 'mongo': one_mongo}
        except Exception as e:
            logger.error(f"Erreur récupération hybride simple: {e}")
            raise

    def get_code_postal_and_polluant(self) -> dict:
        """
        Récupère le code postal et le polluant depuis SQL et MongoDB
        Returns:
            dict: {'sql_code_postal': ..., 'sql_polluant': ..., 'mongo_code_postal': ..., 'mongo_polluant': ...}
        """
        try:
            pg_data = self.get_pg_data()
            one_sql = pg_data[0] if pg_data else None

            mongo_data = self.get_mongo_episodes()
            one_mongo = mongo_data[0] if mongo_data else None

            return {
                'sql_code_postal': one_sql['code_zone'] if one_sql else None,
                'sql_polluant': one_sql['no2'] if one_sql else None,  # exemple: NO2
                'mongo_code_postal': one_mongo['code_insee'] if one_mongo else None,
                'mongo_polluant': one_mongo['polluant'] if one_mongo else None
            }
        except Exception as e:
            logger.error(f"Erreur récupération code postal/polluant: {e}")
            raise

def main():
    """Fonction principale avec arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description='Récupération hybride PostgreSQL/MongoDB')
    
    # Filtres de données
    parser.add_argument('--zone', help='Code zone (ex: 972, 21100)', type=str)
    parser.add_argument('--date-debut', help='Date début (YYYY-MM-DD)', type=str)
    parser.add_argument('--date-fin', help='Date fin (YYYY-MM-DD)', type=str)
    parser.add_argument('--polluants', help='Polluants (ex: NO2,O3,PM10)', type=str)
    
    # Configuration bases
    parser.add_argument('--pg-host', default='localhost', help='Hôte PostgreSQL')
    parser.add_argument('--pg-database', default='qualite_air', help='Base PostgreSQL')
    parser.add_argument('--pg-user', default='postgres', help='Utilisateur PostgreSQL')
    parser.add_argument('--mongo-uri', default='mongodb://localhost:27017/', help='URI MongoDB')
    parser.add_argument('--mongo-database', default='pollution_data', help='Base MongoDB')
    
    # Export
    parser.add_argument('--format', choices=['json', 'csv', 'excel'], default='json', 
                       help='Format de sortie')
    parser.add_argument('--output', help='Fichier de sortie', type=str)
    
    args = parser.parse_args()
    
    # Configuration
    config = DataRetrievalConfig(
        pg_host=args.pg_host,
        pg_database=args.pg_database,
        pg_user=args.pg_user,
        pg_password=os.getenv('DB_PASSWORD', ''),
        mongo_uri=args.mongo_uri,
        mongo_database=args.mongo_database,
        zone_filter=args.zone,
        date_debut=args.date_debut,
        date_fin=args.date_fin,
        polluants=args.polluants.split(',') if args.polluants else None,
        output_format=args.format,
        output_file=args.output
    )
    
    # Exécution
    try:
        with HybridDataRetriever(config) as retriever:
            output_file = retriever.run_hybrid_retrieval()
            print(f"✅ Récupération terminée: {output_file}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()