from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import os

router = APIRouter()

@router.get("/hybride/echantillon", response_class=JSONResponse)
def donnees_croisees(
    limit: int = Query(3, ge=1, le=100, description="Nombre de résultats à retourner"),
    zone: str = Query(None, description="Code zone/INSEE (optionnel)"),
    polluant: str = Query(None, description="Code polluant (optionnel)")
):
    # Connexion PostgreSQL
    pg_conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", 5432),
        database=os.getenv("PG_DATABASE", "postgres"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "")
    )
    pg_cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Construction dynamique de la requête SQL
    sql = "SELECT * FROM indices_qualite_air_consolides"
    filters = []
    params = []
    if zone:
        filters.append("code_zone = %s")
        params.append(zone)
    if polluant:
        filters.append("(code_no2 = %s OR code_o3 = %s OR code_pm10 = %s OR code_pm25 = %s OR code_so2 = %s)")
        params += [polluant]*5
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += f" LIMIT {limit}"
    pg_cursor.execute(sql, params)
    pg_data = pg_cursor.fetchall()
    pg_cursor.close()
    pg_conn.close()

    # Connexion MongoDB
    mongo_client = MongoClient(os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/"))
    mongo_db = mongo_client[os.getenv("MONGO_DATABASE", "pollution")]
    mongo_coll = mongo_db["EPIS_POLLUTION"]
    mongo_query = {}
    if zone:
        mongo_query["properties.code_insee"] = zone
    if polluant:
        mongo_query["properties.polluant"] = polluant
    mongo_data = list(mongo_coll.find(mongo_query, {"_id": 0}).limit(limit))
    mongo_client.close()

    return {
        "pgsql": pg_data,
        "mongo": mongo_data
    }
