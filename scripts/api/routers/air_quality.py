from fastapi import Depends, APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from routers.auth import get_current_user
from security.rate_limiting import public_rate_limit, private_rate_limit
from security.input_validation import QualiteAirQuery, EpisodesQuery
from logger import log_api_call
from fastapi.responses import StreamingResponse
import io
import csv

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

class StationCreate(BaseModel):
    nom_station: str
    code_station: str
    commune: str
    code_insee: str
    latitude: float = None
    longitude: float = None
    altitude: int = None

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

# ========== FUNCTIONS HELPERS ==========
def require_admin_role(current_user: dict = Depends(get_current_user)):
    """
    Vérification du rôle administrateur pour les opérations sensibles.
    
    Contrôle d'accès pour les endpoints nécessitant des privilèges administrateur.
    Utilisé pour la création/modification de stations, paramètres système, etc.
    
    Args:
        current_user (dict): Utilisateur actuel authentifié via JWT
        
    Returns:
        dict: Données utilisateur si admin
        
    Raises:
        HTTPException: 403 si l'utilisateur n'est pas administrateur
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="🔒 Droits administrateur requis pour cette action"
        )
    return current_user


@router.get("/qualite-air",
    summary="📊 Données publiques",
    description="🆓 Accès libre aux données essentielles pour découvrir notre service",
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
    """
    Endpoint public pour consultation des données de qualité de l'air.
    
    Accès libre aux mesures de pollution issues de PostgreSQL.
    Permet la découverte du service et l'attraction d'utilisateurs.
    
    Args:
        request: Objet Request FastAPI
        query: Paramètres de filtrage validés (code INSEE, polluant, station, limite)
        
    Returns:
        dict: Données de pollution filtrées avec métadonnées
        
    Filtres disponibles:
        - code_insee: Code postal/INSEE de la commune
        - code_polluant: Type de polluant (PM10, PM25, NO2, O3, SO2)
        - station: Nom partiel de la station de mesure
        - limit: Nombre maximum de résultats (défaut: 50, max: 100)
    """
    try:
        # Logging de l'appel API pour monitoring et analytics
        log_api_call("/api/qualite-air/qualite-air", "anonymous", query.dict()) 
        
        # Connexion à la base de données PostgreSQL
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construction sécurisée de la requête SQL avec filtres optionnels
        # Base query avec jointure implicite sur table qualite_air
        sql = "SELECT id, code_insee, code_polluant, valeur, qualite_globale, station_nom FROM qualite_air WHERE 1=1"
        params = {}
        
        # Application des filtres selon les paramètres fournis
        if query.code_insee:
            sql += " AND code_insee = %(code_insee)s"  # Filtrage par commune
            params['code_insee'] = query.code_insee
            
        if query.code_polluant:
            sql += " AND code_polluant = %(code_polluant)s"  # Filtrage par type de polluant
            params['code_polluant'] = query.code_polluant
            
        if query.station:
            sql += " AND station_nom ILIKE %(station)s"  # Recherche partielle sur nom station
            params['station'] = f"%{query.station}%"
        
        # Limitation du nombre de résultats pour performance
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
        log_api_call("/api/qualite-air/qualite-air", "anonymous", query.dict(), success=False)
        return {"error": f"Erreur BDD: {str(e)}"}
    

@router.get("/episodes-pollution", 
    summary="🌍 Alertes géolocalisées",
    description="🆓 Épisodes de pollution géolocalisés en temps réel - Consultation libre")
@public_rate_limit()
def get_episodes_pollution_public(
    request: Request,
    query: EpisodesQuery = Depends()
):
    """Accès libre - Épisodes de pollution (MongoDB)"""
    try:
        log_api_call("/api/qualite-air/episodes-pollution", "anonymous", query.dict())

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
            "message": "Données publiques - Épisodes de pollution géolocalisés",
            "source": "MongoDB EPIS_POLLUTION",
            "acces": "Libre - Aucune authentification requise",
            "count": len(documents),
            "filtres_appliques": {
                "aasqa": query.aasqa or "Tous",
                "date_debut": query.date_debut or "Non spécifiée",
                "date_fin": query.date_fin or "Non spécifiée",
                "limite": query.limit
            },
            "data": documents
        }
    except Exception as e:
        log_api_call("/api/qualite-air/episodes-pollution", "anonymous", query.dict(), success=False)
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB EPIS_POLLUTION: {str(e)}")
    

@router.get("/moyennes-journalieres",
    summary="📊 Historique scraping", 
    description="🆓 Moyennes journalières extraites par scraping - Aperçu de nos capacités")
@public_rate_limit()
def get_moyennes_scraping(
    request: Request,
    polluant: Optional[str] = None,
    commune: Optional[str] = None,
    limite: int = 50
):
    """Récupère données de scraping depuis MongoDB"""
    
    try:
        # DEBUG - Vérifier connexion MongoDB
        print(f"🔍 DEBUG: Tentative connexion MongoDB...")
        print(f"🔍 DEBUG: MONGO_DB type: {type(MONGO_DB)}")
        
        collection = MONGO_DB["MOY_JOURNALIERE"]
        print(f"🔍 DEBUG: Collection récupérée: {collection}")
        
        # Test simple count
        total_count = collection.count_documents({})
        print(f"🔍 DEBUG: Total documents dans MOY_JOURNALIERE: {total_count}")
        
        # Si count OK, continuer...
        mongo_filter = {}
        if polluant:
            mongo_filter["polluant"] = polluant
            
        documents = list(collection.find(mongo_filter).limit(limite))
        print(f"🔍 DEBUG: Documents trouvés: {len(documents)}")
        
        # Conversion ObjectId
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        
        return {
            "debug_info": f"Collection MOY_JOURNALIERE - {total_count} docs total",
            "source_donnees": "Scraping Géod'Air → MongoDB",
            "collection": "MOY_JOURNALIERE",
            "filtres": {"polluant": polluant, "limite": limite},
            "resultats": len(documents),
            "donnees": documents[:5]  # Limite à 5 pour debug
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"❌ ERROR type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")




@router.get("/indices-aasqa",
    summary="📋 Données AASQA CSV",
    description="🔐 Accès sécurisé aux données AASQA au format CSV - Authentification requise")
@private_rate_limit()
def get_indices_aasqa_csv(
    request: Request,
    aasqa: Optional[int] = None,
    commune: Optional[str] = None,
    limite: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Affiche indices AASQA depuis PostgreSQL au format CSV - Accès sécurisé"""
    try:
        log_api_call("/api/qualite-air/indices-aasqa", current_user["username"], {
            "aasqa": aasqa,
            "commune": commune,
            "limite": limite
        })
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construction requête avec filtres
        where_conditions = []
        params = []
        
        if aasqa:
            where_conditions.append("aasqa = %s")
            params.append(aasqa)
            
        if commune:
            where_conditions.append("lib_zone ILIKE %s")
            params.append(f"%{commune}%")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Requête principale
        query = f"""
            SELECT 
                aasqa,
                lib_zone as zone,
                date_ech,
                lib_qual as qualite_air,
                coul_qual as couleur_indice,
                code_qual as code_qualite,
                x_wgs84 as longitude,
                y_wgs84 as latitude,
                source,
                date_maj
            FROM indices_qualite_air_consolides 
            {where_clause}
            ORDER BY date_ech DESC, lib_zone
            LIMIT %s
        """
        
        params.append(limite)
        cursor.execute(query, params)
        resultats = cursor.fetchall()
        
        # Création du CSV en format texte
        csv_lines = []
        
        # En-têtes CSV
        headers = ['aasqa', 'zone', 'date_ech', 'qualite_air', 'couleur_indice', 
                  'code_qualite', 'longitude', 'latitude', 'source', 'date_maj']
        csv_lines.append(','.join(headers))
        
        # Données CSV
        for row in resultats:
            row_values = [str(row[field]) if row[field] is not None else '' for field in headers]
            csv_lines.append(','.join(row_values))
        
        csv_content = '\n'.join(csv_lines)
        
        # Statistiques complémentaires
        total_query = f"""
            SELECT COUNT(*) as total
            FROM indices_qualite_air_consolides 
            {where_clause.replace('LIMIT %s', '')}        """
        
        cursor.execute(total_query, params[:-1])  # Sans le LIMIT
        total_count = cursor.fetchone()['total']
        
        return {
            "source_donnees": "PostgreSQL table indices_qualite_air_consolides",
            "origine_fichiers": "CSV AASQA consolidés importés",
            "methode_extraction": "Import CSV → PostgreSQL → API → Format CSV",
            "acces_securise": {
                "utilisateur": current_user["username"],
                "role": current_user.get("role", "user"),
                "authentification": "JWT requis"
            },
            "filtres_appliques": {
                "aasqa": aasqa or "Tous",
                "commune": commune or "Toutes",
                "limite": limite
            },
            "statistiques": {
                "total_disponible": total_count,
                "resultats_affiches": len(resultats),
                "format": "CSV text"
            },
            "donnees_csv": csv_content,
            "exemple_usage": {
                "copier_coller": "Copiez le contenu 'donnees_csv' dans un fichier .csv",
                "excel": "Importez directement dans Excel",
                "analyse": "Utilisez avec pandas, R, ou autres outils data"
            }
        }
        
    except Exception as e:
        log_api_call("/api/qualite-air/indices-aasqa", current_user["username"], {
            "aasqa": aasqa
        }, success=False)
        raise HTTPException(status_code=500, detail=f"Erreur PostgreSQL indices_qualite_air_consolides: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()