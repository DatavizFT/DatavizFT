"""
Application Layer - Couche Application
=======================================

Contient l'orchestration et les cas d'usage métier.
Cette couche coordonne les entités du domaine pour réaliser
les fonctionnalités demandées par les utilisateurs.

Responsabilités :
- Implémenter les cas d'usage métier
- Orchestrer les entités du domaine
- Coordonner les appels aux repositories
- Gérer les transactions
- Convertir entre couches (DTOs)

Principes :
- Pas de logique métier (délégation au domaine)
- Orchestration uniquement
- Gestion des erreurs applicatives
- Point d'entrée pour les interfaces
"""

from .use_cases import *
from .services import *

__all__ = [
    # Use Cases seront exportés automatiquement
    # Services seront exportés automatiquement  
]