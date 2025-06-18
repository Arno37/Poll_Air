from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import air_quality, auth
from security.rate_limiting import setup_rate_limiting

app = FastAPI(
    title="🌐 API Qualité de l'Air - Sécurisée OWASP",
    description="""
    API de consultation des données de pollution atmosphérique en France et Métropole.
    
    ## 🔒 Authentification
    - **Accès libre** : Données de base PostgreSQL
    - **Accès privé** : Données MongoDB (JWT requis)
        
    ## 📊 Sources de données
    - **PostgreSQL** : Table `qualite_air` avec indices de qualité par station
    - **MongoDB** : Collection d'épisodes de pollution géolocalisés
    
    ## 🛡️ Sécurité OWASP
    - JWT Authentication : Contrôle d'accès
    - Rate Limiting : Protection anti-DDoS
    - Input Validation : Protection injection SQL
    
    """,
    version="1.0.0",
)

# Configuration Rate Limiting
setup_rate_limiting(app)

# Configuration CORS basique
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/auth", tags=["🔒 Authentification"])
app.include_router(air_quality.router, prefix="/api", tags=["🌐 Qualité de l'Air"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
