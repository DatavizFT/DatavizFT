"""
Domain Repositories - Interfaces Repository
===========================================

Interfaces définissant les contrats d'accès aux données.
Ces interfaces appartiennent au domaine et sont implémentées
dans la couche infrastructure.

Repositories disponibles :
- JobRepository : Interface pour l'accès aux offres d'emploi
- CompetenceRepository : Interface pour l'accès aux compétences
- StatsRepository : Interface pour l'accès aux statistiques
"""

from .job_repository import JobRepository
from .competence_repository import CompetenceRepository
from .stats_repository import StatsRepository

__all__ = [
    "JobRepository",
    "CompetenceRepository",
    "StatsRepository",
]