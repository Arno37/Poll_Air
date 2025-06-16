from fastapi import APIRouter
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient

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
print(MONGO_CLIENT)

router = APIRouter(prefix="/qualite-air", tags=["Qualité de l'air"])

@router.get("/")
def get_mesures():
    return {"message": "Route qualité air fonctionne !"}

@router.get("/communes")
def get_communes():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT code_insee, nom_commune, assqa_code, departement FROM communes")
        communes = cursor.fetchall()
        cursor.close()
        conn.close()
        return list(communes)
    except Exception as e:
        return {"error": f"Erreur BDD: {str(e)}"}

@router.get("/polluants")
def get_polluants():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT code_polluant, unite_mesure FROM polluants")
        polluants = cursor.fetchall()
        cursor.close()
        conn.close()
        return list(polluants)
    except Exception as e:
        return {"error": f"Erreur BDD: {str(e)}"} 
    
@router.get("/mesures/{code_insee}")
def get_mesures_by_commune(code_insee: str):
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, code_insee, code_polluant, valeur, qualite_globale, station_nom FROM qualite_air WHERE code_insee = %s", (code_insee,))
        mesures = cursor.fetchall()
        cursor.close()
        conn.close()
        return list(mesures)
    except Exception as e:
        return {"error": f"Erreur BDD: {str(e)}"}
    
@router.get("/mongodb-data")
def get_mongodb_data():
    try:
        # Accès à une collection (par exemple "mesures")
        collection = MONGO_DB["EPIS_POLLUTION"]  
        
        # Requête MongoDB (équivalent SELECT * FROM table)
        documents = list(collection.find({}))
        
        # Conversion des ObjectId en string pour JSON
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            
        return documents
    except Exception as e:
        return {"error": f"Erreur MongoDB: {str(e)}"}