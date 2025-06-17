from fastapi import FastAPI
from routers.air_quality import router as qualite_air_router
from routers.auth import router as auth_router

# Création de l'app
app = FastAPI(
   title="🌬️ API Qualité de l'Air",
    description="""
    API de consultation des données de pollution atmosphérique en France et Métropole.
    
    **Sources de données:**
    - PostgreSQL : Indices de qualité de l'air par station
    - MongoDB : Épisodes de pollution géolocalisés
    
    **Authentification:** JWT Bearer Token
    """,
    version="1.0.0"
)

# 🔗 INCLUSION DU ROUTER (étape cruciale)
app.include_router(auth_router)
app.include_router(qualite_air_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)