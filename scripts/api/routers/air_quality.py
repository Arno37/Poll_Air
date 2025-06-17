from fastapi import Depends, APIRouter
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from routers.auth import get_current_user

load_dotenv()

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

router = APIRouter(prefix="/qualite-air", tags=["Qualité de l'air"])


@router.get("/qualite-air",
    summary="📊 Données publiques",
    description="Accès libre aux informations de base",)
def get_qualite_air_public():
    """Accès libre - Données de qualité de l'air (PostgreSQL)"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, code_insee, code_polluant, valeur, qualite_globale, station_nom FROM qualite_air LIMIT 50")
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
    summary="🔒 Épisodes de pollution",
    description="Données MongoDB - Authentification requise",
    )
def get_episodes_pollution_private(current_user: dict = Depends(get_current_user)):
    """Accès protégé - Épisodes de pollution (MongoDB)"""
    try:
        collection = MONGO_DB["EPIS_POLLUTION"]
        documents = list(collection.find({}).limit(20))
        
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

