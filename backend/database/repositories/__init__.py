"""
Database Repositories - Couches d'accès aux données
Définit les repositories pour chaque entité métier
"""

from .offres import OffresRepository
from .competences import CompetencesRepository  
from .stats import StatsRepository

# API publique des repositories
__all__ = [
    "OffresRepository",
    "CompetencesRepository",
    "StatsRepository", 
]