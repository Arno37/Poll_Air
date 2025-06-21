"""
Module de validation et sécurisation des entrées utilisateur.

Ce module fournit des classes Pydantic pour valider les paramètres des requêtes
API et des fonctions pour sécuriser les données contre les injections SQL.

Classes:
    QualiteAirQuery: Validation des paramètres pour les endpoints de qualité de l'air
    EpisodesQuery: Validation des paramètres pour les endpoints d'épisodes de pollution

Functions:
    secure_sql_params: Sécurisation des paramètres SQL contre l'injection
"""

from pydantic import BaseModel, validator
from typing import Optional
import re

class QualiteAirQuery(BaseModel):
    """
    Modèle de validation pour les requêtes de qualité de l'air.
    
    Valide et sécurise les paramètres d'entrée pour les endpoints
    qui récupèrent des données de pollution atmosphérique.
    
    Attributes:
        code_insee (str, optional): Code INSEE commune (5 chiffres)
        code_polluant (str, optional): Code polluant ('PM10', 'PM25', 'NO2', 'O3', 'SO2')
        station (str, optional): Nom de la station de mesure (max 100 chars)
        limit (int, optional): Nombre max de résultats (1-100, défaut: 50)
        
    Validators:
        - code_insee: Format 5 chiffres exactement
        - code_polluant: Liste fermée des polluants autorisés
        - station: Longueur limitée pour éviter l'overflow
        - limit: Borne les résultats pour éviter la surcharge serveur
    """
    code_insee: Optional[str] = None
    code_polluant: Optional[str] = None
    station: Optional[str] = None
    limit: Optional[int] = 50
    
    @validator('code_insee')
    def validate_code_insee(cls, v):
        if v and not re.match(r'^\d{5}$', v):
            raise ValueError('Code INSEE invalide (5 chiffres attendus)')
        return v
    
    @validator('code_polluant')
    def validate_polluant(cls, v):
        allowed = ['PM10', 'PM25', 'NO2', 'O3', 'SO2']
        if v and v not in allowed:
            raise ValueError(f'Polluant invalide. Autorisés: {allowed}')
        return v
    
    @validator('station')
    def validate_station(cls, v):
        if v and len(v) > 100:
            raise ValueError('Nom de station trop long (max 100 caractères)')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v and (v < 1 or v > 100):
            raise ValueError('Limite doit être entre 1 et 100')
        return v

class EpisodesQuery(BaseModel):
    """
    Modèle de validation pour les requêtes d'épisodes de pollution.
    
    Valide les paramètres pour rechercher des épisodes de pollution
    dans la base de données des associations AASQA.
    
    Attributes:
        aasqa (str, optional): Code AASQA (lettres/chiffres, max 10 chars)
        date_debut (str, optional): Date début période (format YYYY-MM-DD)
        date_fin (str, optional): Date fin période (format YYYY-MM-DD)
        limit (int, optional): Nombre max résultats (1-50, défaut: 20)
        
    Validators:
        - aasqa: Format alphanumérique strict
        - dates: Format ISO strict (YYYY-MM-DD)
        - limit: Borné plus strictement que qualité air (épisodes moins fréquents)
    """
    aasqa: Optional[str] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    limit: Optional[int] = 20
    
    @validator('aasqa')
    def validate_aasqa(cls, v):
        if v and not re.match(r'^[A-Z0-9]{1,10}$', v):
            raise ValueError('Code AASQA invalide (lettres/chiffres, max 10 car.)')
        return v
    
    @validator('date_debut', 'date_fin')
    def validate_date(cls, v):
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Format date invalide (YYYY-MM-DD attendu)')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v and (v < 1 or v > 50):
            raise ValueError('Limite doit être entre 1 et 50')
        return v

def secure_sql_params(query_dict: dict) -> dict:
    """
    Sécurise les paramètres SQL contre les injections et attaques.
    
    Cette fonction applique un échappement basique des caractères dangereux
    dans les paramètres qui seront utilisés dans des requêtes SQL.
    
    Args:
        query_dict (dict): Dictionnaire des paramètres de requête
        
    Returns:
        dict: Paramètres sécurisés avec caractères dangereux échappés
        
    Security Measures:
        - Échappement des guillemets simples (protection injection SQL)
        - Suppression des points-virgules (prévention requêtes multiples)
        - Conversion en chaîne pour éviter l'injection par type
        
    Note:
        Cette fonction fournit une protection basique. L'utilisation de
        requêtes préparées (parameterized queries) reste la méthode recommandée.
    """
    secured_params = {}
    for key, value in query_dict.items():
        if value is not None:
            # Échapper les caractères dangereux
            secured_value = str(value).replace("'", "''").replace(";", "")
            secured_params[key] = secured_value
    return secured_params
