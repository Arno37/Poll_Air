from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from routers.auth import get_current_user
from security.rate_limiting import public_rate_limit, private_rate_limit
from logger import log_api_call

load_dotenv()
router = APIRouter()

# MODÈLES PYDANTIC
class ProfilCreate(BaseModel):
    """
    Modèle de données pour la création d'un profil utilisateur.
    
    Utilisé pour valider les données d'inscription lors de la création
    d'un nouveau profil dans le système de recommandations.
    
    Attributes:
        email (EmailStr): Adresse email unique de l'utilisateur
        type_profil (str): Catégorie de profil ('sportif', 'sensible', 'parent', 'senior')
        age_groupe (str, optional): Tranche d'âge de l'utilisateur
        pathologies (List[str]): Liste des pathologies déclarées (asthme, allergies, etc.)
        activites_pratiquees (List[str]): Liste des activités pratiquées (course, vélo, etc.)
        commune_residence (str): Code INSEE de la commune de résidence
        niveau_sensibilite (str): Niveau de sensibilité à la pollution ('faible', 'moyen', 'élevé')
    """
    email: EmailStr
    type_profil: str  # 'sportif', 'sensible', 'parent', 'senior'
    age_groupe: Optional[str] = None
    pathologies: List[str] = []
    activites_pratiquees: List[str] = []
    commune_residence: str
    niveau_sensibilite: str = "moyen"

class RecommandationResponse(BaseModel):
    """
    Modèle de réponse pour les recommandations personnalisées.
    
    Structure de données retournée par l'endpoint de recommandations
    contenant tous les éléments nécessaires à l'affichage côté client.
    
    Attributes:
        profil_type (str): Type de profil pour lequel la recommandation est calculée
        commune (str): Code INSEE de la commune concernée
        niveau_pollution (str): Niveau global de pollution ('bon', 'moyen', 'dégradé', etc.)
        conseil (str): Message de recommandation principal
        niveau_urgence (int): Niveau d'urgence de 1 (info) à 5 (critique)
        icone (str): Nom de l'icône à afficher dans l'interface
        polluants_details (dict): Détails par polluant avec seuils et conseils spécifiques
    """
    profil_type: str
    commune: str
    niveau_pollution: str
    conseil: str
    niveau_urgence: int
    icone: str
    polluants_details: dict

# Configuration BDD (même que air_quality.py)
DATABASE_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "database": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "port": os.getenv("PG_PORT")
}

@router.post("/profils/create",
    summary="👤 Inscription gratuite ",
    description="🆓 Créez votre profil pour accéder aux recommandations personnalisées")
@public_rate_limit()
def create_profil(profil: ProfilCreate, request: Request):
    """
    Créer un nouveau profil utilisateur dans le système.
    
    Cette fonction publique permet à tout utilisateur de créer gratuitement
    un profil personnalisé pour recevoir des recommandations sur la qualité de l'air.
    
    Args:
        profil (ProfilCreate): Données du profil à créer (email, type, commune, etc.)
        request (Request): Objet requête FastAPI pour le logging
        
    Returns:
        dict: Confirmation de création avec ID du profil généré
        
    Raises:
        HTTPException 400: Email déjà utilisé ou commune inexistante
        HTTPException 500: Erreur serveur/base de données
        
    Security:
        - Endpoint public (pas d'authentification requise)
        - Rate limiting appliqué pour éviter le spam
        - Validation de l'existence de la commune
        - Contrainte d'unicité sur l'email
        
    Business Logic:
        - Vérifie que la commune existe dans la table communes
        - Crée le profil avec les paramètres fournis
        - Retourne l'ID du profil pour usage ultérieur
    """
    
    try:
        log_api_call("/api/profils/create", "anonymous", {"type_profil": profil.type_profil})
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier que la commune existe
        cursor.execute("SELECT code_insee FROM communes WHERE code_insee = %s", (profil.commune_residence,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Commune {profil.commune_residence} non trouvée")
        
        # Insérer le profil
        cursor.execute("""
            INSERT INTO profils_utilisateurs 
            (email, type_profil, age_groupe, pathologies, activites_pratiquees, 
             commune_residence, niveau_sensibilite)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            profil.email, profil.type_profil, profil.age_groupe,
            profil.pathologies, profil.activites_pratiquees,
            profil.commune_residence, profil.niveau_sensibilite
        ))
        
        profil_id = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "message": "✅ Profil créé avec succès",
            "profil_id": profil_id,
            "type_profil": profil.type_profil,
            "commune": profil.commune_residence
        }
        
    except psycopg2.IntegrityError as e:
        if "email" in str(e):
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        raise HTTPException(status_code=400, detail="Erreur création profil")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/recommandations/{profil_id}",
    summary="🎯 Conseils personnalisés",
    description="🔐 Recommandations adaptées à votre profil et environnement",
    response_model=RecommandationResponse)
@private_rate_limit()
def get_recommandations(
    profil_id: int, 
    request: Request,
    type_activite: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir des recommandations personnalisées basées sur le profil et la pollution actuelle.
    
    Cette fonction premium calcule des recommandations adaptées au profil utilisateur
    en tenant compte de la pollution actuelle dans sa commune de résidence.
    
    Args:
        profil_id (int): ID du profil utilisateur
        request (Request): Objet requête FastAPI pour le logging
        type_activite (str, optional): Type d'activité prévue ('sport', 'sortie', etc.)
        current_user (dict): Utilisateur authentifié (injecté par Depends)
        
    Returns:
        RecommandationResponse: Recommandations personnalisées avec détails polluants
        
    Raises:
        HTTPException 404: Profil non trouvé ou pas de données pollution
        HTTPException 500: Erreur serveur/base de données
        
    Security:
        - Authentification requise (endpoint premium)
        - Rate limiting pour éviter l'abus
        - Logging des accès utilisateur
        
    Business Logic:
        - Récupère le profil et sa commune
        - Obtient les données pollution récentes (24h)
        - Calcule le niveau pollution personnalisé via seuils adaptés
        - Sélectionne la recommandation appropriée selon profil/activité
        - Enrichit avec détails par polluant et conseils spécifiques
    """
    
    try:
        log_api_call("/api/recommandations", current_user["username"], {"profil_id": profil_id})
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Récupérer le profil
        cursor.execute("""
            SELECT type_profil, commune_residence, niveau_sensibilite 
            FROM profils_utilisateurs 
            WHERE id = %s
        """, (profil_id,))
        
        profil = cursor.fetchone()
        if not profil:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        type_profil, commune, sensibilite = profil['type_profil'], profil['commune_residence'], profil['niveau_sensibilite']
        
        # Récupérer pollution actuelle de la commune
        cursor.execute("""
            SELECT p.code_polluant, qa.valeur, qa.niveau_qualite
            FROM qualite_air qa
            JOIN polluants p ON qa.polluant_id = p.id
            WHERE qa.code_insee = %s
            AND qa.date_mesure >= CURRENT_DATE - INTERVAL '1 day'
            ORDER BY qa.date_mesure DESC
            LIMIT 10
        """, (commune,))
        
        pollution_data = cursor.fetchall()
        if not pollution_data:
            raise HTTPException(status_code=404, detail="Pas de données pollution récentes pour cette commune")
        
        # Calculer niveau pollution personnalisé
        niveau_global = calculate_personal_pollution_level(cursor, type_profil, pollution_data)
        
        # Récupérer recommandation adaptée
        activite_filter = type_activite or 'sortie_generale'
        cursor.execute("""
            SELECT conseil, niveau_urgence, icone
            FROM recommandations_base
            WHERE profil_cible = %s 
            AND niveau_pollution = %s
            AND (type_activite LIKE %s OR type_activite = 'sortie_generale')
            ORDER BY niveau_urgence DESC
            LIMIT 1
        """, (type_profil, niveau_global, f'%{activite_filter.split("_")[0]}%'))
        
        recommandation = cursor.fetchone()
        if not recommandation:
            # Recommandation par défaut
            recommandation = {
                'conseil': "Consultez les données de pollution avant toute activité", 
                'niveau_urgence': 2, 
                'icone': "warning"
            }
        
        # Détails polluants avec seuils personnalisés
        polluants_details = {}
        for row in pollution_data:
            polluant, valeur, niveau = row['code_polluant'], row['valeur'], row['niveau_qualite']
            cursor.execute("""
                SELECT seuil_info, seuil_alerte, conseil_depassement
                FROM seuils_personnalises
                WHERE profil_type = %s AND polluant = %s
            """, (type_profil, polluant))
            
            seuil_data = cursor.fetchone()
            if seuil_data:
                seuil_info, seuil_alerte, conseil = seuil_data['seuil_info'], seuil_data['seuil_alerte'], seuil_data['conseil_depassement']
                status = "bon" if valeur < seuil_info else "alerte" if valeur < seuil_alerte else "danger"
                polluants_details[polluant] = {
                    "valeur": valeur,
                    "seuil_info": seuil_info,
                    "seuil_alerte": seuil_alerte,
                    "status": status,
                    "conseil": conseil if status != "bon" else "Aucune précaution particulière"
                }
        
        return {
            "profil_type": type_profil,
            "commune": commune,
            "niveau_pollution": niveau_global,
            "conseil": recommandation['conseil'],
            "niveau_urgence": recommandation['niveau_urgence'],
            "icone": recommandation['icone'],
            "polluants_details": polluants_details
        }
        
    except Exception as e:
        log_api_call("/api/recommandations", current_user["username"], {"profil_id": profil_id}, success=False)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def calculate_personal_pollution_level(cursor, type_profil, pollution_data):
    """
    Calcule le niveau de pollution personnalisé selon le profil utilisateur.
    
    Cette fonction applique des seuils personnalisés selon le type de profil
    (sportif, sensible, parent, senior) pour évaluer le niveau de pollution
    réel ressenti par l'utilisateur.
    
    Args:
        cursor: Curseur de base de données PostgreSQL
        type_profil (str): Type de profil ('sportif', 'sensible', 'parent', 'senior')
        pollution_data (list): Liste des mesures de pollution actuelles
        
    Returns:
        str: Niveau de pollution personnalisé ('bon', 'moyen', 'degrade', 'mauvais', 'tres_mauvais')
        
    Logic:
        - Récupère les seuils personnalisés pour chaque polluant
        - Compare les valeurs mesurées aux seuils du profil
        - Retourne le niveau le plus élevé (plus restrictif)
    """
    max_level = "bon"
    level_priority = {"bon": 0, "moyen": 1, "degrade": 2, "mauvais": 3, "tres_mauvais": 4}
    
    for row in pollution_data:
        polluant, valeur = row['code_polluant'], row['valeur']
        # Récupérer seuils personnalisés
        cursor.execute("""
            SELECT seuil_info, seuil_alerte
            FROM seuils_personnalises
            WHERE profil_type = %s AND polluant = %s
        """, (type_profil, polluant))
        
        seuils = cursor.fetchone()
        if seuils:
            seuil_info, seuil_alerte = seuils['seuil_info'], seuils['seuil_alerte']
            
            if valeur >= seuil_alerte:
                niveau_perso = "tres_mauvais"
            elif valeur >= seuil_info * 1.5:
                niveau_perso = "mauvais"
            elif valeur >= seuil_info:
                niveau_perso = "degrade"
            elif valeur >= seuil_info * 0.7:
                niveau_perso = "moyen"
            else:
                niveau_perso = "bon"
              # Garder le niveau le plus élevé
            if level_priority[niveau_perso] > level_priority[max_level]:
                max_level = niveau_perso
    
    return max_level

@router.get("/profils/{profil_id}",
    summary="👤 Gestion profil",
    description="🔐 Accédez et gérez vos informations personnelles")
@private_rate_limit()
def get_profil(profil_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    """
    Récupérer les informations complètes d'un profil utilisateur.
    
    Cette fonction premium permet à un utilisateur authentifié de consulter
    toutes les informations de son profil stockées dans le système.
    
    Args:
        profil_id (int): ID du profil à récupérer
        request (Request): Objet requête FastAPI pour le logging
        current_user (dict): Utilisateur authentifié (injecté par Depends)
        
    Returns:
        dict: Informations complètes du profil (email, type, commune, etc.)
        
    Raises:
        HTTPException 404: Profil non trouvé
        HTTPException 500: Erreur serveur/base de données
        
    Security:
        - Authentification requise (endpoint premium)
        - Rate limiting appliqué
        - Logging des accès pour audit
        
    Note:
        - Retourne toutes les données sensibles du profil
        - Utilisé pour la gestion de compte utilisateur
    """
    
    try:
        log_api_call("/api/profils", current_user["username"], {"profil_id": profil_id})
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, email, type_profil, age_groupe, pathologies, 
                   activites_pratiquees, commune_residence, niveau_sensibilite,
                   created_at
            FROM profils_utilisateurs 
            WHERE id = %s
        """, (profil_id,))
        
        profil = cursor.fetchone()
        if not profil:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        return dict(profil)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        cursor.close()
        conn.close()