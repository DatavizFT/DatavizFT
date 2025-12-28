"""
Routes API pour la collecte des offres
"""

from fastapi import APIRouter, BackgroundTasks, Request
from datetime import datetime

from backend_v2.application.services import CollectionService


router = APIRouter(prefix="/collection", tags=["collection"])


@router.post("/trigger")
async def trigger_collection(background_tasks: BackgroundTasks):
    """
    Déclencher manuellement une collecte des offres
    La collecte s'exécute en arrière-plan
    """
    service = CollectionService()

    async def run_collection():
        await service.collect_all_sources(max_offres_per_source=None)  # Toutes les offres

    background_tasks.add_task(run_collection)

    return {
        "status": "started",
        "message": "Collecte lancee en arriere-plan",
        "timestamp": datetime.now()
    }


@router.get("/status")
async def get_collection_status(request: Request):
    """Obtenir le statut du scheduler de collecte"""
    # Récupérer le scheduler depuis l'état de l'application
    collection_scheduler = getattr(request.app.state, "collection_scheduler", None)

    if not collection_scheduler:
        return {
            "status": "disabled",
            "message": "Scheduler non active"
        }

    next_run = collection_scheduler.get_next_run_time()

    return {
        "status": "active",
        "next_scheduled_run": next_run,
        "schedule": "Tous les jours a 02:00"
    }


@router.get("/history")
async def get_collection_history(limit: int = 10):
    """
    Obtenir l'historique des collectes
    """
    service = CollectionService()

    # Récupérer les dernières exécutions
    cursor = service.db.collection_executions.find().sort("timestamp", -1).limit(limit)
    executions = await cursor.to_list(length=limit)

    # Formater pour la réponse
    history = []
    for exec in executions:
        history.append({
            "timestamp": exec.get("timestamp"),
            "total_nouvelles_offres": exec.get("total_nouvelles_offres", 0),
            "total_doublons": exec.get("total_doublons", 0),
            "sources": exec.get("sources", {}),
            "extraction_competences": exec.get("extraction_competences"),
        })

    return {
        "history": history,
        "count": len(history)
    }
