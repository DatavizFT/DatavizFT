"""
MongoDB Documents et Schemas - Structures MongoDB spécifiques
Définit les documents MongoDB et leurs validations
"""

from .documents import (
    CompetenceDocument,
    OffreDocument,
    StatsDocument,
)
from .schemas import (
    COMPETENCE_SCHEMA,
    OFFRE_SCHEMA,
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
