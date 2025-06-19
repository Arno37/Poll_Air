from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

# Configuration du limiteur
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI):
    """Configuration du rate limiting pour l'application"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter

# Décorateurs prêts à l'emploi
def public_rate_limit():
    """Rate limit pour endpoints publics - 100 requêtes/minute"""
    return limiter.limit("100/minute")

def private_rate_limit():
    """Rate limit pour endpoints privés - 50 requêtes/minute (plus restrictif)"""
    return limiter.limit("50/minute")

def admin_rate_limit():
    """Rate limit pour endpoints admin - 200 requêtes/minute"""
    return limiter.limit("200/minute")
