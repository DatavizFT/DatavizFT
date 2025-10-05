"""
Backend DatavizFT - Module principal
Architecture modulaire pour les pipelines de données
"""

# Exports principaux depuis models
from .models import (
    COMPETENCES_REFERENTIEL,
    CATEGORIES_COMPETENCES,
    NB_CATEGORIES,
    NB_COMPETENCES_TOTAL
)

# Exports principaux depuis pipelines
from .pipelines import (
    PipelineM1805,
    run_pipelineFT,
    run_pipeline_avec_limite,
    lister_pipelines_disponibles
)

# Exports principaux depuis tools (classes les plus utilisées)
from .tools import (
    FranceTravailAPIClient,
    CompetenceAnalyzer,
    FileManager,
    charger_config_pipeline
)

# API publique simplifiée
__all__ = [
    # Référentiel de compétences
    'COMPETENCES_REFERENTIEL',
    'CATEGORIES_COMPETENCES', 
    'NB_CATEGORIES',
    'NB_COMPETENCES_TOTAL',
    
    # Pipelines
    'PipelineM1805',
    'run_pipelineFT',
    'run_pipeline_avec_limite',
    'lister_pipelines_disponibles',
    
    # Outils essentiels
    'FranceTravailAPIClient',
    'CompetenceAnalyzer',
    'FileManager',
    'charger_config_pipeline'
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
        "pipelines_disponibles": list(lister_pipelines_disponibles().keys())
    }

# Ajout à l'API publique
__all__.append('info_systeme')