"""
Configuration centralisée pour la récupération hybride de données
"""

import os
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DatabaseConfig:
    """Configuration des bases de données"""
    
    # PostgreSQL
    PG_HOST: str = os.getenv('DB_HOST', 'localhost')
    PG_PORT: int = int(os.getenv('DB_PORT', '5432'))
    PG_DATABASE: str = os.getenv('DB_NAME', 'qualite_air')
    PG_USER: str = os.getenv('DB_USER', 'postgres')
    PG_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # MongoDB
    MONGO_URI: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGO_DATABASE: str = os.getenv('MONGODB_DB', 'pollution_data')
    
    # Collections MongoDB
    COLLECTION_EPISODES: str = 'EPIS_POLLUTION'
    COLLECTION_MOYENNES: str = 'MOY_JOURNALIERE'
    
    # Limites de requête
    MAX_RECORDS_PG: int = 10000
    MAX_RECORDS_MONGO: int = 5000
    
    # Timeout connexions (secondes)
    CONNECTION_TIMEOUT: int = 30

# Seuils de qualité de l'air (µg/m³)
SEUILS_POLLUTION = {
    'NO2': {'information': 200, 'alerte': 400},
    'O3': {'information': 180, 'alerte': 240},
    'PM10': {'information': 50, 'alerte': 80},
    'PM25': {'information': 35, 'alerte': 50},
    'SO2': {'information': 300, 'alerte': 500}
}

# Mapping des codes régionaux
CODES_REGIONS = {
    '21': 'Bourgogne-Franche-Comté',
    '76': 'Normandie', 
    '972': 'Martinique',
    '33': 'Nouvelle-Aquitaine',
    '75': 'Île-de-France'
}

# Organismes AASQA
ORGANISMES_AASQA = {
    'ATMO BFC': 'Bourgogne-Franche-Comté',
    'ATMO NORMANDIE': 'Normandie',
    'MADININAIR': 'Martinique',
    'ATMO NOUVELLE-AQUITAINE': 'Nouvelle-Aquitaine',
    'AIRPARIF': 'Île-de-France'
}