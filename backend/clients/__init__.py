"""
Backend clients - Clients pour APIs externes
Gestion des connexions vers les services externes (France Travail, etc.)
"""

# Import du client principal France Travail
from .france_travail import FranceTravailAPIClient

# Exports principaux
__all__ = ["FranceTravailAPIClient"]

# Métadonnées
__version__ = "1.0.0"
__author__ = "DatavizFT Team"
