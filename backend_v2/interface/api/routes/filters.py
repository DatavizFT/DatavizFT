"""
Routes API pour les filtres du dashboard
"""

from fastapi import APIRouter, Depends
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.interface.api.schemas.responses import CityResponse, SourceResponse

router = APIRouter(prefix="/filters", tags=["filters"])


def get_db() -> MongoDBConnection:
    """Dependency injection pour la connexion MongoDB"""
    return MongoDBConnection()


@router.get("/cities", response_model=list[CityResponse])
async def get_top_cities(
    limit: int = 5,
    db: MongoDBConnection = Depends(get_db)
) -> list[CityResponse]:
    """
    Retourne les top N villes avec le plus d'offres d'emploi

    Args:
        limit: Nombre de villes à retourner (défaut: 5)
    """
    pipeline = [
        {"$match": {"lieu_travail.libelle": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$lieu_travail.libelle",
            "job_count": {"$sum": 1}
        }},
        {"$sort": {"job_count": -1}},
        {"$limit": limit}
    ]

    collection = db.async_db["offres"]
    results = await collection.aggregate(pipeline).to_list(length=limit)

    return [
        CityResponse(name=r["_id"], job_count=r["job_count"])
        for r in results
    ]


@router.get("/sources", response_model=list[SourceResponse])
async def get_sources(
    db: MongoDBConnection = Depends(get_db)
) -> list[SourceResponse]:
    """
    Retourne les sources de données disponibles avec leur nombre d'offres
    """
    pipeline = [
        {"$group": {
            "_id": "$source",
            "job_count": {"$sum": 1}
        }},
        {"$sort": {"job_count": -1}}
    ]

    collection = db.async_db["offres"]
    results = await collection.aggregate(pipeline).to_list(length=10)

    return [
        SourceResponse(name=r["_id"] or "unknown", job_count=r["job_count"])
        for r in results
        if r["_id"] is not None
    ]
