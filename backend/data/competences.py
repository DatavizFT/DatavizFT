"""
Compétences - Référentiel des compétences techniques
Chargement et exposition du référentiel de compétences depuis competences.json
"""

import json
from pathlib import Path


def charger_competences_referentiel() -> dict[str, list[str]]:
    """
    Charge le référentiel de compétences depuis le fichier JSON

    Returns:
        Dict contenant les compétences organisées par catégorie

    Raises:
        FileNotFoundError: Si le fichier competences.json n'existe pas
        json.JSONDecodeError: Si le fichier JSON est malformé
    """
    try:
        chemin_competences = Path(__file__).parent / "competences.json"
        with open(chemin_competences, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fichier competences.json non trouvé dans backend/data/")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return {}


# Chargement du référentiel au niveau module
COMPETENCES_REFERENTIEL = charger_competences_referentiel()

# Métadonnées dérivées
CATEGORIES_COMPETENCES = list(COMPETENCES_REFERENTIEL.keys())
NB_CATEGORIES = len(COMPETENCES_REFERENTIEL)
NB_COMPETENCES_TOTAL = sum(
    len(competences) for competences in COMPETENCES_REFERENTIEL.values()
)


# Fonction utilitaire pour validation
def valider_referentiel() -> bool:
    """
    Valide la cohérence du référentiel de compétences

    Returns:
        True si le référentiel est valide, False sinon
    """
    if not COMPETENCES_REFERENTIEL:
        return False

    for _categorie, competences in COMPETENCES_REFERENTIEL.items():
        if not isinstance(competences, list):
            return False
        if len(competences) == 0:
            return False

    return True


def obtenir_toutes_competences() -> list[str]:
    """
    Obtient la liste de toutes les compétences (toutes catégories confondues)

    Returns:
        Liste plate de toutes les compétences
    """
    toutes_competences = []
    for competences in COMPETENCES_REFERENTIEL.values():
        toutes_competences.extend(competences)
    return toutes_competences


def rechercher_competence(terme: str) -> list[tuple[str, str]]:
    """
    Recherche une compétence dans le référentiel

    Args:
        terme: Terme de recherche (insensible à la casse)

    Returns:
        Liste de tuples (categorie, competence) correspondant au terme
    """
    resultats = []
    terme_lower = terme.lower()

    for categorie, competences in COMPETENCES_REFERENTIEL.items():
        for competence in competences:
            if terme_lower in competence.lower():
                resultats.append((categorie, competence))

    return resultats
