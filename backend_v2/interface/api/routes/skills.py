"""
Routes API pour l'évolution des compétences
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.interface.api.schemas.responses import (
    SkillEvolutionPoint,
    SkillEvolutionResponse,
)

router = APIRouter(prefix="/skills", tags=["skills"])


def get_db() -> MongoDBConnection:
    """Dependency injection pour la connexion MongoDB"""
    return MongoDBConnection()


@router.get("/evolution", response_model=SkillEvolutionResponse)
async def get_skills_evolution(
    source: str | None = Query(None, description="Filtrer par source (francetravail, adzuna)"),
    city: str | None = Query(None, description="Filtrer par ville"),
    start_date: date | None = Query(None, description="Date de début (défaut: 30 jours avant)"),
    end_date: date | None = Query(None, description="Date de fin (défaut: aujourd'hui)"),
    top_n: int = Query(10, ge=1, le=50, description="Nombre de compétences à afficher"),
    db: MongoDBConnection = Depends(get_db)
) -> SkillEvolutionResponse:
    """
    Retourne l'évolution journalière des compétences les plus recherchées

    Args:
        source: Filtrer par source de données
        city: Filtrer par ville
        start_date: Date de début de la période
        end_date: Date de fin de la période
        top_n: Nombre de top compétences à retourner
    """
    # Dates par défaut: 30 derniers jours
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # Construire le filtre de base
    match_filter: dict = {}

    # Filtre par date - convertir en datetime pour MongoDB
    from datetime import datetime as dt
    start_datetime = dt.combine(start_date, dt.min.time())
    end_datetime = dt.combine(end_date, dt.max.time())

    match_filter["date_creation"] = {
        "$gte": start_datetime,
        "$lte": end_datetime
    }

    # Filtre par source
    if source:
        match_filter["source"] = source

    # Filtre par ville
    if city:
        match_filter["lieu_travail.libelle"] = {"$regex": city, "$options": "i"}

    collection = db.async_db["offres"]

    # Pipeline pour obtenir les top N compétences sur la période
    top_skills_pipeline = [
        {"$match": match_filter},
        {"$unwind": "$competences_extraites"},
        {"$group": {
            "_id": "$competences_extraites",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": top_n}
    ]

    top_skills_result = await collection.aggregate(top_skills_pipeline).to_list(length=top_n)
    top_skills = [r["_id"] for r in top_skills_result]

    # Si pas de compétences trouvées, retourner une réponse vide
    if not top_skills:
        return SkillEvolutionResponse(
            data=[],
            total_jobs=0,
            period_start=start_date,
            period_end=end_date,
            filters={"source": source, "city": city}
        )

    # Pipeline pour l'évolution journalière des top compétences
    evolution_pipeline = [
        {"$match": match_filter},
        {"$unwind": "$competences_extraites"},
        {"$match": {"competences_extraites": {"$in": top_skills}}},
        {"$addFields": {
            "date_str": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": {"$toDate": "$date_creation"}
                }
            }
        }},
        {"$group": {
            "_id": {
                "date": "$date_str",
                "skill": "$competences_extraites"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1, "_id.skill": 1}}
    ]

    evolution_result = await collection.aggregate(evolution_pipeline).to_list(length=1000)

    # Compter le total des offres
    total_jobs = await collection.count_documents(match_filter)

    # Formater les résultats
    data = [
        SkillEvolutionPoint(
            date=date.fromisoformat(r["_id"]["date"]),
            skill=r["_id"]["skill"],
            count=r["count"]
        )
        for r in evolution_result
    ]

    return SkillEvolutionResponse(
        data=data,
        total_jobs=total_jobs,
        period_start=start_date,
        period_end=end_date,
        filters={"source": source, "city": city}
    )
