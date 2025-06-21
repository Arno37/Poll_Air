"""
Module de logging centralisé pour l'API de qualité de l'air.

Ce module fournit un système de logging unifié pour tracer les appels API,
les tentatives de connexion et les erreurs dans un format JSON structuré.

Functions:
    log_api_call: Enregistre les appels d'endpoints API
    log_login: Enregistre les tentatives de connexion

Configuration:
    - Logs sauvegardés dans logs/api.log
    - Format JSON pour faciliter l'analyse
    - Niveaux: INFO (succès), ERROR (échecs API), WARNING (connexions échouées)
"""

import logging
import json
from datetime import datetime
import os


os.makedirs("logs", exist_ok=True)

# Configuration simple du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),  # Fichier
        logging.StreamHandler()               # Console
    ]
)

logger = logging.getLogger("API")

def log_api_call(endpoint: str, user: str = "anonymous", params: dict = None, success: bool = True):
    """
    Enregistre un appel d'endpoint API avec contexte utilisateur.
    
    Cette fonction trace tous les accès aux endpoints pour audit et monitoring.
    Utilisée systématiquement dans tous les routers pour traçabilité.
    
    Args:
        endpoint (str): Chemin de l'endpoint appelé (ex: "/api/qualite-air")
        user (str): Nom d'utilisateur ou "anonymous" pour les endpoints publics
        params (dict, optional): Paramètres de la requête (anonymisés si sensibles)
        success (bool): True si succès, False si erreur
        
    Logs:
        - INFO level: Appels réussis
        - ERROR level: Appels échoués
        - Format JSON avec timestamp ISO
        
    Privacy:
        - Ne log jamais de mots de passe ou tokens
        - Paramètres sensibles doivent être filtrés en amont
    """
    log_data = {
        "endpoint": endpoint,
        "user": user,
        "params": params or {},
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        logger.info(f"API_CALL: {json.dumps(log_data)}")
    else:
        logger.error(f"API_ERROR: {json.dumps(log_data)}")

def log_login(username: str, success: bool, ip: str = "unknown"):
    """
    Enregistre les tentatives de connexion pour audit de sécurité.
    
    Cette fonction trace toutes les tentatives d'authentification,
    succès comme échecs, pour détecter les attaques par force brute.
    
    Args:
        username (str): Nom d'utilisateur (peut être erroné en cas d'échec)
        success (bool): True si connexion réussie, False sinon
        ip (str): Adresse IP source (pour géolocalisation/blocage)
        
    Logs:
        - INFO level: Connexions réussies
        - WARNING level: Tentatives échouées (potentielles attaques)
        - Format JSON avec timestamp pour analyse automatisée
        
    Security:
        - Utilisé pour détecter les patterns d'attaque
        - Base pour l'implémentation future de rate limiting par IP
        - Peut déclencher des alertes en cas de pic d'échecs
    """
    log_data = {
        "username": username,
        "success": success,
        "ip": ip,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        logger.info(f"LOGIN_SUCCESS: {json.dumps(log_data)}")
    else:
        logger.warning(f"LOGIN_FAILED: {json.dumps(log_data)}")