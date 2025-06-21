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
        if v and not re.match(r'^[A-Z0-9]{2,10}$', v):
            raise ValueError('Code AASQA invalide')
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

class StationCreateValidation(BaseModel):
    """Validation pour la création de station (admin)"""
    nom_station: str
    code_station: str
    commune: str
    code_insee: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    
    @validator('nom_station')
    def validate_nom_station(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nom de station requis (min 2 caractères)')
        if len(v) > 100:
            raise ValueError('Nom de station trop long (max 100 caractères)')
        # Empêcher caractères potentiellement dangereux
        if re.search(r'[<>"\';]', v):
            raise ValueError('Caractères non autorisés dans le nom de station')
        return v.strip()
    
    @validator('code_station')
    def validate_code_station(cls, v):
        if not re.match(r'^[A-Z0-9_-]{3,20}$', v):
            raise ValueError('Code station invalide (3-20 caractères alphanumériques)')
        return v
    
    @validator('code_insee')
    def validate_code_insee(cls, v):
        if not re.match(r'^\d{5}$', v):
            raise ValueError('Code INSEE invalide (5 chiffres)')
        return v
    
    @validator('commune')
    def validate_commune(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nom de commune requis')
        if len(v) > 100:
            raise ValueError('Nom de commune trop long')
        if re.search(r'[<>"\';]', v):
            raise ValueError('Caractères non autorisés dans le nom de commune')
        return v.strip()
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude invalide (entre -90 et 90)')
        return v
    
    @validator('longitude') 
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude invalide (entre -180 et 180)')
        return v
    
    @validator('altitude')
    def validate_altitude(cls, v):
        if v is not None and (v < -500 or v > 5000):
            raise ValueError('Altitude invalide (entre -500 et 5000m)')
        return v

def validate_sql_params(query_dict: dict) -> dict:
    """
    Valide les paramètres avant usage SQL
    Note: L'échappement SQL est fait automatiquement par psycopg2
    """
    validated_params = {}
    for key, value in query_dict.items():
        if value is not None:
            # Validation supplémentaire pour longueurs maximales
            str_value = str(value)
            if len(str_value) > 100:  # Limite raisonnable
                raise ValueError(f"Paramètre {key} trop long (max 100 caractères)")
            validated_params[key] = value  # Garder type original
    return validated_params

# Note: La vraie protection contre injection SQL se fait via les requêtes paramétrées
# de psycopg2 dans air_quality.py avec cursor.execute(sql, params)