"""
Schémas de réponse pour l'API Dashboard
"""

from datetime import date
from pydantic import BaseModel


class SkillEvolutionPoint(BaseModel):
    """Point de données pour l'évolution d'une compétence"""
    date: date
    skill: str
    count: int


class SkillEvolutionResponse(BaseModel):
    """Réponse pour l'endpoint évolution des compétences"""
    data: list[SkillEvolutionPoint]
    total_jobs: int
    period_start: date
    period_end: date
    filters: dict


class CityResponse(BaseModel):
    """Réponse pour une ville"""
    name: str
    job_count: int


class SourceResponse(BaseModel):
    """Réponse pour une source de données"""
    name: str
    job_count: int
