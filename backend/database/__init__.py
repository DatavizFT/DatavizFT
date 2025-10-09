"""
Backend Database - Couche d'accès aux données MongoDB
Gestion des connexions, repositories et opérations MongoDB
"""

from .connection import (
    DatabaseConnection,
    close_database,
    get_database,
    init_database,
)
from .repositories import (
    CompetencesRepository,
    OffresRepository,
    StatsRepository,
)

# API publique du module database
__all__ = [
    # Connexion
    "DatabaseConnection",
    "get_database",
    "init_database",
    "close_database",
    # Repositories
    "OffresRepository",
    "CompetencesRepository",
    "StatsRepository",
]
