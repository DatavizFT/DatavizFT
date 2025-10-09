"""
Backend Data - Données statiques et référentiels
Centralise toutes les données de référence du projet
"""

from .competences import (
    CATEGORIES_COMPETENCES,
    COMPETENCES_REFERENTIEL,
    NB_CATEGORIES,
    NB_COMPETENCES_TOTAL,
    charger_competences_referentiel,
)

# API publique du module data
__all__ = [
    "COMPETENCES_REFERENTIEL",
    "CATEGORIES_COMPETENCES",
    "NB_CATEGORIES",
    "NB_COMPETENCES_TOTAL",
    "charger_competences_referentiel",
]
