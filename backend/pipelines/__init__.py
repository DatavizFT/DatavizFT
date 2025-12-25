"""
Backend pipelines - Pipelines de traitement des données
Expose tous les pipelines disponibles et leurs fonctions d'entrée
"""

# Import de la nouvelle architecture modulaire
from .instances.france_travail_pipeline import FranceTravailPipeline

# Exports principaux
__all__ = [
    # Nouvelle architecture modulaire
    "FranceTravailPipeline",
    # Classes de base (si nécessaires à l'externe)
]

# Configuration des pipelines disponibles
PIPELINES_DISPONIBLES = {
    "M1805": {
        "nom": "France Travail - Études et développement informatique",
        "code_rome": "M1805",
        "classe": FranceTravailPipeline,
        "description": "Collecte et analyse des offres d'emploi pour les développeurs",
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
    return pipeline_info["classe"] if pipeline_info else None


# Ajout aux exports
__all__.extend(
    ["lister_pipelines_disponibles", "obtenir_pipeline", "PIPELINES_DISPONIBLES"]
)

# Métadonnées
__version__ = "1.0.0"
