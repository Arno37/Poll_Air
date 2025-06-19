from pydantic import BaseModel, validator
from typing import Optional
import re

class QualiteAirQuery(BaseModel):
    """Validation pour les requêtes de qualité de l'air"""
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
    """Validation pour les requêtes d'épisodes de pollution"""
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
    Sécurise les paramètres SQL contre l'injection
    Échappe les caractères dangereux
    """
    secured_params = {}
    for key, value in query_dict.items():
        if value is not None:
            # Échapper les caractères dangereux
            secured_value = str(value).replace("'", "''").replace(";", "")
            secured_params[key] = secured_value
    return secured_params
