"""
Module de limitation de taux (rate limiting) pour l'API.

Ce module implémente une protection contre l'abus d'endpoints en limitant
le nombre de requêtes par minute selon le type d'endpoint et l'utilisateur.

Classes/Functions:
    setup_rate_limiting: Configuration du rate limiting sur l'app FastAPI
    public_rate_limit: Décorateur pour endpoints publics (100 req/min)
    private_rate_limit: Décorateur pour endpoints premium (50 req/min)
    admin_rate_limit: Décorateur pour endpoints admin (200 req/min)

Strategy:
    - Endpoints publics: limite généreuse pour l'acquisition
    - Endpoints premium: limite plus stricte pour éviter l'abus
    - Endpoints admin: limite élevée pour les opérations de maintenance
    - Limitation par adresse IP source
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

# Configuration du limiteur
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI):
    """
    Configure le système de rate limiting pour l'application FastAPI.
    
    Attache le limiteur à l'application et configure le gestionnaire
    d'erreurs pour les dépassements de limite.
    
    Args:
        app (FastAPI): Instance de l'application FastAPI
        
    Returns:
        Limiter: Instance du limiteur configuré
        
    Note:
        Doit être appelé lors de l'initialisation de l'app dans main.py
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter

# Décorateurs prêts à l'emploi pour différents niveaux d'accès
def public_rate_limit():
    """
    Rate limit pour endpoints publics d'acquisition.
    
    Limite généreuse (100 requêtes/minute) pour encourager l'adoption
    et permettre une utilisation normale des fonctionnalités gratuites.
    
    Usage: @public_rate_limit() au-dessus des endpoints publics
    """
    return limiter.limit("100/minute")

def private_rate_limit():
    """
    Rate limit pour endpoints premium/privés.
    
    Limite plus restrictive (50 requêtes/minute) pour éviter l'abus
    des fonctionnalités premium par des scripts automatisés.
    
    Usage: @private_rate_limit() au-dessus des endpoints authentifiés
    """
    return limiter.limit("50/minute")

def admin_rate_limit():
    """
    Rate limit pour endpoints d'administration.
    
    Limite élevée (200 requêtes/minute) pour permettre les opérations
    de maintenance et la gestion intensive du système.
    
    Usage: @admin_rate_limit() au-dessus des endpoints admin
    """
    return limiter.limit("200/minute")
