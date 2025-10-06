"""
Data Loader - Chargement des données de référence
Gestion centralisée des référentiels de compétences, configurations, etc.
"""

from typing import Any


def charger_config_pipeline(nom_pipeline: str) -> dict[str, Any]:
    """
    Charge la configuration spécifique d'un pipeline

    Args:
        nom_pipeline: Nom du pipeline à configurer

    Returns:
        Dict contenant la configuration du pipeline
    """
    configs_default = {
        "france_travail_m1805": {
            "code_rome": "M1805",
            "rate_limit_ms": 120,
            "page_size": 150,
            "user_agent": "DatavizFT-Collector/1.0",
        }
    }

    # Possibilité d'étendre avec des fichiers de config externes
    return configs_default.get(nom_pipeline, {})


def valider_referentiel_competences(competences: dict[str, Any]) -> bool:
    """
    Valide la structure du référentiel de compétences

    Args:
        competences: Dictionnaire des compétences à valider

    Returns:
        True si la structure est valide, False sinon
    """
    categories_requises = [
        "langages",
        "frameworks_frontend",
        "frameworks_backend",
        "frameworks_mobile",
        "outils_devops",
        "bases_de_donnees",
        "data_ia",
        "securite",
        "cloud",
        "tests_qualite",
        "environnements_ide",
        "api_integration",
        "ux_ui_design",
        "collaboration_gestion",
        "systemes_exploitation",
        "methodologies_architecture",
        "formats_protocoles",
        "outils_monitoring",
        "certifications",
    ]

    for categorie in categories_requises:
        if categorie not in competences:
            print(f"❌ Catégorie manquante: {categorie}")
            return False
        if not isinstance(competences[categorie], list):
            print(f"❌ Catégorie {categorie} n'est pas une liste")
            return False

    return True


def obtenir_statistiques_referentiel(competences: dict[str, Any]) -> dict[str, int]:
    """
    Calcule les statistiques du référentiel de compétences

    Args:
        competences: Dictionnaire des compétences

    Returns:
        Dict avec les statistiques (nb_categories, nb_competences_total, etc.)
    """
    if not competences:
        return {"nb_categories": 0, "nb_competences_total": 0}

    stats = {
        "nb_categories": len(competences),
        "nb_competences_total": sum(
            len(comp_list) for comp_list in competences.values()
        ),
    }

    # Ajout des détails par catégorie
    for categorie, comp_list in competences.items():
        stats[f"nb_{categorie}"] = len(comp_list)

    return stats
