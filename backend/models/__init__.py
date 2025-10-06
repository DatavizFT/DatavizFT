"""
Backend models - Structures de données et modèles
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def charger_referentiel_competences() -> dict[str, list[str]]:
    """
    Charge le référentiel de compétences depuis competences.json

    Returns:
        Dict contenant les compétences organisées par catégories
    """
    try:
        chemin_competences = Path(__file__).parent / "competences.json"
        with open(chemin_competences, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fichier competences.json non trouvé dans {Path(__file__).parent}"
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de parsing JSON dans competences.json: {e}")


# Export principal du référentiel de compétences
COMPETENCES_REFERENTIEL = charger_referentiel_competences()

# Export des métadonnées utiles
CATEGORIES_COMPETENCES = list(COMPETENCES_REFERENTIEL.keys())
NB_CATEGORIES = len(CATEGORIES_COMPETENCES)
NB_COMPETENCES_TOTAL = sum(
    len(competences) for competences in COMPETENCES_REFERENTIEL.values()
)

# Exports pour faciliter les imports
__all__ = [
    "COMPETENCES_REFERENTIEL",
    "CATEGORIES_COMPETENCES",
    "NB_CATEGORIES",
    "NB_COMPETENCES_TOTAL",
    "charger_referentiel_competences",
]
