"""
backend_v2/infrastructure/external_apis/__init__.py
Exports publics des clients d'APIs externes
"""

from .france_travail_api import FranceTravailAPIClient

__all__ = ["FranceTravailAPIClient"]
