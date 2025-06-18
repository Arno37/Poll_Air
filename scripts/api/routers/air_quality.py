from fastapi import Depends, APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from routers.auth import get_current_user
from security.rate_limiting import public_rate_limit, private_rate_limit
from security.input_validation import QualiteAirQuery, EpisodesQuery


load_dotenv()
class QualiteAirResponse(BaseModel):
    message: str
    count: int
    data: List[Dict[str, Any]]

class EpisodeResponse(BaseModel):
    message: str
    user: str
    role: str
    count: int
    data: List[Dict[str, Any]]

# Configuration PG
DATABASE_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "database": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "port": os.getenv("PG_PORT")
}

# Configuration MongoDB
MONGO_CLIENT = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
MONGO_DB = MONGO_CLIENT[os.getenv("MONGO_DATABASE")]

router = APIRouter(prefix="/qualite-air")


@router.get("/qualite-air",
    summary="📊 Données publiques",
    description="Accès libre aux informations de base",
    response_model=QualiteAirResponse,
    responses={
        200: {"description": "Données récupérées avec succès"},
        500: {"description": "Erreur de base de données"}
    })
@public_rate_limit()
def get_qualite_air_public(
    request: Request,
    query: QualiteAirQuery = Depends()
):
    """Accès libre - Données de qualité de l'air (PostgreSQL)"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construction sécurisée de la requête
        sql = "SELECT id, code_insee, code_polluant, valeur, qualite_globale, station_nom FROM qualite_air WHERE 1=1"
        params = {}
        
        if query.code_insee:
            sql += " AND code_insee = %(code_insee)s"
            params['code_insee'] = query.code_insee
            
        if query.code_polluant:
            sql += " AND code_polluant = %(code_polluant)s"
            params['code_polluant'] = query.code_polluant
            
        if query.station:
            sql += " AND station_nom ILIKE %(station)s"
            params['station'] = f"%{query.station}%"
        
        sql += f" LIMIT {query.limit}"
        
        cursor.execute(sql, params)
        mesures = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "message": "Données publiques de qualité de l'air",
            "count": len(mesures),
            "data": list(mesures)
        }
    except Exception as e:
        return {"error": f"Erreur BDD: {str(e)}"}

@router.get("/episodes-pollution", 
    summary="🔒 Données privées",
    description="Données MongoDB - Authentification requise",
    )
@private_rate_limit()
def get_episodes_pollution_private(
    request: Request,
    query: EpisodesQuery = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """Accès protégé - Épisodes de pollution (MongoDB)"""
    try:
        collection = MONGO_DB["EPIS_POLLUTION"]
        
        # Construction sécurisée de la requête MongoDB
        mongo_filter = {}
        
        if query.aasqa:
            mongo_filter["aasqa"] = query.aasqa
            
        if query.date_debut:
            mongo_filter["date_ech"] = {"$gte": query.date_debut}
            
        if query.date_fin:
            if "date_ech" in mongo_filter:
                mongo_filter["date_ech"]["$lte"] = query.date_fin
            else:
                mongo_filter["date_ech"] = {"$lte": query.date_fin}
        
        documents = list(collection.find(mongo_filter).limit(query.limit))
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            
        return {
            "message": "Données privées - Épisodes de pollution",
            "user": current_user["username"],
            "role": current_user["role"],
            "count": len(documents),
            "data": documents
        }
    except Exception as e:
        return {"error": f"Erreur MongoDB: {str(e)}"}

