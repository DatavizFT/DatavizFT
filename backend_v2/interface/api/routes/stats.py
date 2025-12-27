"""
Routes API pour les statistiques de compétences
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel

from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.infrastructure.repositories.stats_repository_mongodb import StatsRepositoryMongoDB

router = APIRouter(prefix="/stats", tags=["stats"])


def get_db() -> MongoDBConnection:
    """Dependency injection pour la connexion MongoDB"""
    return MongoDBConnection()


# ============= Schémas de réponse =============

class CompetenceStats(BaseModel):
    """Statistiques d'une compétence"""
    competence: str
    nb_occurrences: int
    pourcentage: float


class CategoryStats(BaseModel):
    """Statistiques d'une catégorie"""
    categorie: str
    nb_offres_avec_categorie: int
    pourcentage_offres: float
    nb_technologies_detectees: int
    technologies_populaires: List[CompetenceStats]


class LatestStatsResponse(BaseModel):
    """Réponse pour les dernières statistiques"""
    source: str
    periode_analysee: str
    nb_offres_analysees: int
    top_competences: List[CompetenceStats]
    statistiques_par_categorie: dict


class TendancesResponse(BaseModel):
    """Réponse pour les tendances"""
    croissantes: List[str]
    declinantes: List[str]
    stables: List[str]


class RealtimeStatsResponse(BaseModel):
    """Réponse pour les stats temps réel"""
    periode_analysee: str
    nb_offres_analysees: int
    competences_stats: List[CompetenceStats]
    top_competences: List[str]


# ============= Endpoints =============

@router.get("/latest", response_model=LatestStatsResponse)
async def get_latest_stats(
    db: MongoDBConnection = Depends(get_db)
) -> LatestStatsResponse:
    """
    Récupère les dernières statistiques générées.

    Ces statistiques sont calculées périodiquement par le StatsGenerator.
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    latest = await stats_repo.get_latest_stats()

    if not latest:
        raise HTTPException(
            status_code=404,
            detail="Aucune statistique disponible. Lancez d'abord une collecte."
        )

    return LatestStatsResponse(
        source=latest.get("source", "unknown"),
        periode_analysee=latest.get("periode_analysee", ""),
        nb_offres_analysees=latest.get("nb_offres_analysees", 0),
        top_competences=[
            CompetenceStats(
                competence=c["competence"],
                nb_occurrences=c["nb_occurrences"],
                pourcentage=c["pourcentage"]
            )
            for c in latest.get("top_competences", [])
        ],
        statistiques_par_categorie=latest.get("statistiques_par_categorie", {})
    )


@router.get("/by-period/{periode}")
async def get_stats_by_period(
    periode: str,
    db: MongoDBConnection = Depends(get_db)
):
    """
    Récupère les statistiques d'une période spécifique.

    Args:
        periode: Format "YYYY-MM" (ex: "2024-12")
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    stats = await stats_repo.get_stats_by_periode(periode)

    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune statistique pour la période {periode}"
        )

    # Retirer le _id MongoDB
    if "_id" in stats:
        del stats["_id"]

    return stats


@router.get("/realtime", response_model=RealtimeStatsResponse)
async def get_realtime_stats(
    jours: int = Query(30, ge=1, le=365, description="Nombre de jours à analyser"),
    db: MongoDBConnection = Depends(get_db)
) -> RealtimeStatsResponse:
    """
    Calcule des statistiques temps réel sur les N derniers jours.

    Contrairement aux stats périodiques, celles-ci sont calculées à la volée.
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    stats = await stats_repo.calculate_realtime_stats(jours)

    return RealtimeStatsResponse(
        periode_analysee=stats["periode_analysee"],
        nb_offres_analysees=stats["nb_offres_analysees"],
        competences_stats=[
            CompetenceStats(
                competence=c["competence"],
                nb_occurrences=c["nb_offres"],
                pourcentage=c["pourcentage"]
            )
            for c in stats.get("competences_stats", [])
        ],
        top_competences=stats.get("top_competences", [])
    )


@router.get("/tendances", response_model=TendancesResponse)
async def get_tendances(
    seuil: float = Query(0.1, ge=0, le=1, description="Seuil de croissance (10% par défaut)"),
    db: MongoDBConnection = Depends(get_db)
) -> TendancesResponse:
    """
    Identifie les tendances d'évolution des compétences.

    Compare les 2 dernières périodes pour identifier les compétences
    en croissance, déclin ou stables.
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    tendances = await stats_repo.get_tendances_competences(seuil)

    return TendancesResponse(
        croissantes=tendances["croissantes"],
        declinantes=tendances["declinantes"],
        stables=tendances["stables"]
    )


@router.get("/evolution/{competence}")
async def get_competence_evolution(
    competence: str,
    nb_periodes: int = Query(12, ge=1, le=24, description="Nombre de périodes"),
    db: MongoDBConnection = Depends(get_db)
):
    """
    Récupère l'évolution d'une compétence sur plusieurs périodes.

    Args:
        competence: Nom de la compétence
        nb_periodes: Nombre de périodes à récupérer
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    evolution = await stats_repo.get_evolution_competence(competence, nb_periodes)

    if not evolution:
        raise HTTPException(
            status_code=404,
            detail=f"Pas de données d'évolution pour la compétence '{competence}'"
        )

    return {
        "competence": competence,
        "evolution": evolution
    }


@router.get("/geo")
async def get_stats_geographiques(
    competence: Optional[str] = Query(None, description="Filtrer par compétence"),
    db: MongoDBConnection = Depends(get_db)
):
    """
    Calcule les statistiques géographiques.

    Args:
        competence: Filtrer par compétence spécifique (optionnel)
    """
    stats_repo = StatsRepositoryMongoDB(db.async_db)

    stats_geo = await stats_repo.get_stats_geographiques(competence)

    return stats_geo
