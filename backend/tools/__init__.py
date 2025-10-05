"""
Backend tools - Outils réutilisables pour tous les pipelines
Expose tous les outils nécessaires pour créer des pipelines de données
"""

# Import des classes principales
from .api_client import FranceTravailAPIClient
from .competence_analyzer import CompetenceAnalyzer
from .file_manager import FileManager

# Import des fonctions utilitaires
from .data_loader import charger_config_pipeline, valider_referentiel_competences, obtenir_statistiques_referentiel
from .text_processor import (
    nettoyer_texte,
    extraire_texte_offre, 
    creer_patterns_recherche,
    rechercher_competence_dans_texte
)

# Exports des classes principales (pour faciliter les imports)
__all__ = [
    # Classes principales
    'FranceTravailAPIClient',
    'CompetenceAnalyzer', 
    'FileManager',
    
    # Fonctions de configuration et validation
    'charger_config_pipeline',
    'valider_referentiel_competences',
    'obtenir_statistiques_referentiel',
    
    # Fonctions de traitement de texte
    'nettoyer_texte',
    'extraire_texte_offre',
    'creer_patterns_recherche', 
    'rechercher_competence_dans_texte'
]

# Métadonnées du module tools
__version__ = "1.0.0"
__author__ = "DatavizFT Team"