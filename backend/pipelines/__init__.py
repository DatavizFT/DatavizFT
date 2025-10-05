"""
Backend pipelines - Pipelines de traitement des données
Expose tous les pipelines disponibles et leurs fonctions d'entrée
"""

# Import du pipeline principal M1805
from .france_travail_m1805 import (
    PipelineM1805,
    run_pipelineFT,
    run_pipeline_avec_limite
)

# Exports principaux
__all__ = [
    # Classes de pipelines
    'PipelineM1805',
    
    # Fonctions d'exécution
    'run_pipelineFT',           # Pipeline complet avec vérification 24h
    'run_pipeline_avec_limite'  # Pipeline avec limite d'offres
]

# Configuration des pipelines disponibles
PIPELINES_DISPONIBLES = {
    'M1805': {
        'nom': 'France Travail - Études et développement informatique',
        'code_rome': 'M1805',
        'classe': PipelineM1805,
        'description': 'Collecte et analyse des offres d\'emploi pour les développeurs'
    }
}

# Fonction utilitaire pour lister les pipelines
def lister_pipelines_disponibles():
    """
    Retourne la liste des pipelines disponibles avec leurs informations
    
    Returns:
        Dict des pipelines avec leurs métadonnées
    """
    return PIPELINES_DISPONIBLES

# Fonction pour obtenir un pipeline par son code
def obtenir_pipeline(code_rome: str):
    """
    Obtient une classe de pipeline par son code ROME
    
    Args:
        code_rome: Code ROME du pipeline souhaité
        
    Returns:
        Classe du pipeline ou None si non trouvé
    """
    pipeline_info = PIPELINES_DISPONIBLES.get(code_rome)
    return pipeline_info['classe'] if pipeline_info else None

# Ajout aux exports
__all__.extend(['lister_pipelines_disponibles', 'obtenir_pipeline', 'PIPELINES_DISPONIBLES'])

# Métadonnées
__version__ = "1.0.0"