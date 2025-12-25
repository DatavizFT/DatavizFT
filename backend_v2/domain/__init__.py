"""
Domain Layer - Couche Domaine
==============================

Contient la logique métier pure de l'application.
Cette couche ne dépend d'aucune autre couche et définit :

- Entités métier avec leurs règles business
- Interfaces des repositories (contrats)
- Services domaine pour logique complexe
- Value Objects pour concepts métier
- Événements domaine

Principes :
- Pas de dépendances externes
- Logique métier pure
- Testable unitairement
- Indépendant de la technologie
"""

from .entities import Job
from .repositories import JobRepository

__all__ = [
    # Entités
    "Job",
    #"Competence", 
    #"Statistics",
    # Repositories (interfaces)
    "JobRepository",
    #"CompetenceRepository",
    #"StatisticsRepository",
    "CollectorPipeline",
]