"""
MongoDB Documents et Schemas - Structures MongoDB spécifiques
Définit les documents MongoDB et leurs validations
"""

from .documents import (
    OffreDocument,
    CompetenceDocument,
    StatsDocument,
)
from .schemas import (
    OFFRE_SCHEMA,
    COMPETENCE_SCHEMA,
    STATS_SCHEMA,
    create_collection_with_schema,
)

# API publique des modèles MongoDB
__all__ = [
    # Documents
    "OffreDocument",
    "CompetenceDocument", 
    "StatsDocument",
    # Schemas de validation
    "OFFRE_SCHEMA",
    "COMPETENCE_SCHEMA",
    "STATS_SCHEMA",
    "create_collection_with_schema",
]