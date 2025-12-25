"""
DatavizFT Backend v2 - Architecture Hexagonale
================================================

Architecture moderne démontrant les bonnes pratiques du développement logiciel :
- Domain-Driven Design (DDD)
- Architecture Hexagonale (Ports & Adapters)
- Principes SOLID
- Inversion de dépendance
- Testabilité par design

Structure :
-----------
domain/         - Logique métier pure (entités, interfaces)
application/    - Cas d'usage et orchestration
infrastructure/ - Détails techniques (DB, APIs externes)
interface/      - Points d'entrée (REST API, CLI)
shared/         - Utilitaires partagés
tests/          - Tests par couche

Auteur: DatavizFT
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "DatavizFT"

# Exports principaux
#from .domain.entities import Job, Competence, Statistics
#from .domain.repositories import JobRepository, CompetenceRepository, StatisticsRepository

__all__ = [
    "Job",
    "Competence", 
    "Statistics",
    "JobRepository",
    "CompetenceRepository",
    "StatisticsRepository",
]