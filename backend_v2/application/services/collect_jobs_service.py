"""
CollectJobsService - Service d'application pour la collecte d'offres d'emploi
Orchestre la collecte via un client d'infrastructure (API France Travail ou autre)
"""
from typing import Any, Dict, List, Protocol
from backend_v2.domain.services.CollectorPipeline import CollectorPipeline
from backend_v2.shared import logger

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
        self.logger = logger.bind(service="CollectJobsService")

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
        self.logger.info("Début de la collecte des offres", params=params, page_size=page_size, max_offres=max_offres)
        try:
            jobs = self.job_client.collect_offres_paginated(params, page_size=page_size, max_offres=max_offres)
            self.logger.info("Collecte terminée", nb_offres=len(jobs))
        except Exception as e:
            self.logger.error("Erreur lors de la collecte des offres", error=str(e), params=params)
            raise

        pipeline = CollectorPipeline()
        self.logger.info("Exécution du pipeline de traitement des offres", nb_offres=len(jobs))
        marked_jobs = pipeline.run_pipeline(jobs)
        self.logger.info("Pipeline terminé", nb_offres=len(marked_jobs))

#        for job in marked_jobs:
#            self.logger.info(f"Offre is_new: {job.get('is_new')}")

        return marked_jobs
