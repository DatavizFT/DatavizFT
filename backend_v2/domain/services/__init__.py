"""
Domain Services - Services métier du domaine
=============================================

Services de traitement métier :
- CollectorPipeline : Pipeline de collecte et traitement des offres
- SemanticCompetenceAnalyzer : Extraction de compétences par embeddings
- DeduplicationService : Détection de doublons sémantiques
- StatsGenerator : Générateur de statistiques par compétences
"""

from .CollectorPipeline import CollectorPipeline
from .competence_analyzer import SemanticCompetenceAnalyzer, CompetenceMatch
from .deduplication_service import DeduplicationService
from .stats_generator import StatsGenerator

__all__ = [
    "CollectorPipeline",
    "SemanticCompetenceAnalyzer",
    "CompetenceMatch",
    "DeduplicationService",
    "StatsGenerator",
]
