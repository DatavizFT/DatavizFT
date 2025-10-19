"""
CollectJobsService - Service d'application pour la collecte d'offres d'emploi
Orchestre la collecte via un client d'infrastructure (API France Travail ou autre)
"""
from typing import Any, Dict, List, Protocol

class JobClientProtocol(Protocol):
    def collect_offres_paginated(self, params: Dict[str, Any], page_size: int = 150, max_offres: int | None = None) -> List[Dict[str, Any]]:
        ...

class CollectJobsService:
    """
    Service d'application pour collecter des offres d'emploi depuis n'importe quelle source compatible.
    Le client (infrastructure) doit respecter JobClientProtocol.
    """
    def __init__(self, job_client: JobClientProtocol):
        self.job_client = job_client

    def collect_jobs(self, params: Dict[str, Any], page_size: int = 150, max_offres: int | None = None) -> List[Dict[str, Any]]:
        """
        Collecte les offres d'emploi via le client fourni.
        Args:
            params: paramètres de recherche (ex: codeROME, localisation, etc.)
            page_size: taille de page API
            max_offres: nombre max d'offres à collecter
        Returns:
            Liste d'offres d'emploi (dictionnaires bruts)
        """
        return self.job_client.collect_offres_paginated(params, page_size=page_size, max_offres=max_offres)
