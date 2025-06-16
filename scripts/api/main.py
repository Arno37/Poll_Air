from fastapi import FastAPI
from routers.air_quality import router as qualite_air_router

# Création de l'app
app = FastAPI(title="🌬️ API Qualité de l'Air")

# 🔗 INCLUSION DU ROUTER (étape cruciale)
app.include_router(qualite_air_router)

@app.get("/")
def home():
    return {"message": "API principale fonctionne !"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)