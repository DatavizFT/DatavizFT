"""
Interface Layer - Couche Interface
==================================

Points d'entrée de l'application.
Cette couche expose les fonctionnalités aux utilisateurs
via différents canaux (REST API, CLI, etc.).

Responsabilités :
- Exposer les use cases via REST API
- Valider les entrées utilisateur
- Formater les sorties
- Gérer l'authentification/autorisation
- Documentation API (OpenAPI)

Principes :
- Dépend uniquement de la couche Application
- Transforme les requêtes externes en appels use cases
- Gère la sérialisation/désérialisation
- Point d'entrée unique par type d'interface
"""

from .api import *
from .cli import *

__all__ = [
    # Exports seront définis par les sous-modules
]