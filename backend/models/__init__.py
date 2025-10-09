"""
Backend Models - Modèles de données avec Pydantic
Définit les structures de données pour validation et sérialisation
"""

from .competence import (
    CompetenceModel,
    CompetenceStats,
    CategorieCompetence,
)
from .offre import (
    EntrepriseModel,
    LocalisationModel,
    OffreEmploiModel,
    OffreFranceTravail,
    SalaireModel,
)

# API publique du module models
__all__ = [
    # Modèles offres d'emploi
    "OffreFranceTravail",
    "OffreEmploiModel", 
    "EntrepriseModel",
    "LocalisationModel",
    "SalaireModel",
    # Modèles compétences
    "CompetenceModel",
    "CompetenceStats", 
    "CategorieCompetence",
]
