"""
Infrastructure Layer - Couche Infrastructure
============================================

Contient tous les détails techniques et l'implémentation
des interfaces définies par le domaine.

Responsabilités :
- Implémentation des repositories (MongoDB)
- Clients pour APIs externes (France Travail)
- Configuration système
- Logging et monitoring
- Cache et optimisations

Principes :
- Implémente les interfaces du domaine
- Peut dépendre de toutes les autres couches
- Contient les détails techniques
- Facilement remplaçable
"""

from .database import *
from .config import *

__all__ = [
    # Exports seront définis par les sous-modules
]