from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import air_quality, auth
from security.rate_limiting import setup_rate_limiting
from routers import air_quality, auth, profils

app = FastAPI(
    title="🌍 API Qualité de l'Air - Multi-Sources",
    description="""
    **API de données pollution atmosphérique en France et territoitre Outre-Mer**
    
    ## 🎯 **PARCOURS UTILISATEUR OPTIMISÉ**
    
    ### 🆓 **ÉTAPE 1 (Accès libre)**
    - 📊 **Données pollution de base** : Consultez la qualité de l'air
    - 📈 **Historique scraping** : Explorez nos moyennes journalières  
    - 🗺️ **Couverture régionale** : Vérifiez notre présence géographique
    - 👤 **Inscription gratuite** : Créez votre profil en 2 minutes
    
    ### 🔐 **ÉTAPE 2 (Connexion requise)**
    - 🚨 **Alertes géolocalisées** : Épisodes pollution temps réel
    - 🎯 **Conseils personnalisés** : Recommandations adaptées à votre profil
    - ⚙️ **Gestion compte** : Accès à vos données personnelles
        
    ## 📊 **SOURCES DE DONNÉES HYBRIDES**
    - **PostgreSQL** : Mesures structurées, profils utilisateurs
    - **MongoDB** : Données géospatiales, scraping temps réel
    - **CSV Import** : Indices AASQA régionaux
    
    ## 🛡️ **SÉCURITÉ OWASP**
    - **Rate Limiting** : Protection DDoS différenciée public/privé
    - **JWT Authentication** : Accès sécurisé aux fonctionnalités
    - **Input Validation** : Protection injection SQL systématique
    
    """,
    version="2.0.0",
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
app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(air_quality.router, prefix="/api", tags=["Qualité de l'Air"])
app.include_router(profils.router, prefix="/api", tags=["Profils & Recommandations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
