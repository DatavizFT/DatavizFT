"""
Point d'entrée API FastAPI pour le Dashboard DatavizFT
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_v2.config import Config
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.infrastructure.scheduler import CollectionScheduler
from backend_v2.interface.api.routes import skills, filters, collection, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup: vérifier la connexion MongoDB
    db = MongoDBConnection()
    try:
        # Test de connexion
        await db.async_db.command("ping")
        print("[API] Connexion MongoDB OK")
    except Exception as e:
        print(f"[API] Erreur connexion MongoDB: {e}")

    # Démarrer le scheduler de collecte automatique
    try:
        scheduler = CollectionScheduler()
        scheduler.start(run_immediately=False)  # Ne pas lancer immédiatement
        next_run = scheduler.get_next_run_time()
        print(f"[API] Scheduler de collecte demarre - Prochaine execution: {next_run}")

        # Stocker dans l'état de l'application
        app.state.collection_scheduler = scheduler
    except Exception as e:
        print(f"[API] Erreur demarrage scheduler: {e}")
        app.state.collection_scheduler = None

    yield

    # Shutdown: arrêter le scheduler et fermer les connexions
    if hasattr(app.state, "collection_scheduler") and app.state.collection_scheduler:
        app.state.collection_scheduler.stop()
        print("[API] Scheduler arrete")

    print("[API] Fermeture des connexions...")


app = FastAPI(
    title="DatavizFT Dashboard API",
    description="API REST pour le dashboard de visualisation des compétences IT",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration CORS - inclure le port Vite (5173)
cors_origins = Config.CORS_ORIGINS + ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(skills.router, prefix="/api")
app.include_router(filters.router, prefix="/api")
app.include_router(collection.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/")
async def root():
    """Route racine - Health check"""
    return {
        "status": "ok",
        "app": Config.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = MongoDBConnection()
    try:
        await db.async_db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend_v2.interface.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.is_development()
    )
