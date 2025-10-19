"""
backend_v2/infrastructure/clients/__init__.py
Exports publics des clients externes (API, services tiers)
"""

from .france_travail_api import FranceTravailAPIClient

__all__ = ["FranceTravailAPIClient"]
