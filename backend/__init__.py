"""
Backend DatavizFT - Module principal
Architecture modulaire pour les pipelines de données
"""

# Exports principaux depuis les nouveaux modules
from .clients import FranceTravailAPIClient
from .data import (
    CATEGORIES_COMPETENCES,
    COMPETENCES_REFERENTIEL,
    NB_CATEGORIES,
    NB_COMPETENCES_TOTAL,
)

# Exports principaux depuis pipelines
from .pipelines import (
    PIPELINES_DISPONIBLES,
    FranceTravailPipeline,
    lister_pipelines_disponibles,
    obtenir_pipeline,
)
from .tools import CompetenceAnalyzer, FileManager, charger_config_pipeline

# API publique simplifiée
__all__ = [
    # Référentiel de compétences
    "COMPETENCES_REFERENTIEL",
    "CATEGORIES_COMPETENCES",
    "NB_CATEGORIES",
    "NB_COMPETENCES_TOTAL",
    # Pipelines
    "FranceTravailPipeline",
    "lister_pipelines_disponibles",
    "obtenir_pipeline",
    "PIPELINES_DISPONIBLES",
    # Outils essentiels
    "FranceTravailAPIClient",
    "CompetenceAnalyzer",
    "FileManager",
    "charger_config_pipeline",
]

# Métadonnées
__version__ = "1.0.0"
__author__ = "DatavizFT Team"
__description__ = "Pipeline de collecte et d'analyse des offres d'emploi France Travail"


# Fonction utilitaire pour avoir un aperçu du système
def info_systeme():
    """
    Affiche les informations principales du système DatavizFT

    Returns:
        Dict avec les informations système
    """
    return {
        "version": __version__,
        "description": __description__,
        "nb_categories_competences": NB_CATEGORIES,
        "nb_competences_total": NB_COMPETENCES_TOTAL,
        "pipelines_disponibles": list(lister_pipelines_disponibles().keys()),
    }


# Ajout à l'API publique
__all__.append("info_systeme")
