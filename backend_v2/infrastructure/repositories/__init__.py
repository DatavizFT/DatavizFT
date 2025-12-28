"""
Infrastructure Repositories - Implémentations MongoDB
======================================================

Implémentations concrètes des interfaces de repositories définies dans le domaine.
Ces implémentations utilisent MongoDB via Motor (async).

Repositories disponibles :
- JobRepositoryMongoDB : Implémentation MongoDB pour les offres d'emploi
- CompetenceRepositoryMongoDB : Implémentation MongoDB pour les compétences
- StatsRepositoryMongoDB : Implémentation MongoDB pour les statistiques
"""

from .job_repository_mongodb import JobRepositoryMongoDB
from .competence_repository_mongodb import CompetenceRepositoryMongoDB
from .stats_repository_mongodb import StatsRepositoryMongoDB

__all__ = [
    "JobRepositoryMongoDB",
    "CompetenceRepositoryMongoDB",
    "StatsRepositoryMongoDB",
]
