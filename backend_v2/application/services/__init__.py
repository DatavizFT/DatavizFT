"""
Application Services - Services Application
===========================================

Services de coordination et d'orchestration.
Ces services coordonnent plusieurs use cases ou gèrent
des aspects transversaux de l'application.

Services disponibles :
- JobService : Coordination des opérations sur les offres
- CompetenceService : Coordination des opérations sur les compétences
- DataVizService : Coordination pour la génération de visualisations
- CollectionService : Collecte automatisée multi-sources
"""

from .collection_service import CollectionService

__all__ = [
    "CollectionService",
]