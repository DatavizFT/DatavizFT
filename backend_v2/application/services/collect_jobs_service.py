"""
CollectJobsService - Service d'application pour la collecte d'offres d'emploi
Orchestre la collecte via un client d'infrastructure (API France Travail ou autre)
"""
from typing import Any, Dict, List, Protocol
from backend_v2.domain.entities.job import Job
from backend_v2.domain.services.CollectorPipeline import CollectorPipeline
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.domain.repositories.job_repository import JobRepository
from backend_v2.shared import logger

class JobClientProtocol(Protocol):
    def collect_offres_paginated(self, params: Dict[str, Any], page_size: int = 150, max_offres: int | None = None) -> List[Dict[str, Any]]:
        ...

class CollectJobsService:
    """
    Service d'application pour collecter des offres d'emploi depuis n'importe quelle source compatible.
    Le client (infrastructure) doit respecter JobClientProtocol.
    """
    def __init__(
        self,
        job_client: JobClientProtocol,
        job_repo: JobRepository,
        pipeline: CollectorPipeline = None
    ):
        self.job_client = job_client
        self.job_repo = job_repo
        self.pipeline = pipeline or CollectorPipeline()
        self.logger = logger.bind(service="CollectJobsService")

    async def collect_jobs(self, params: Dict[str, Any], page_size: int = 150, max_offres: int | None = None) -> List[Job]:
        """
        Collecte les offres d'emploi via le client fourni.
        1. récupération des offres exposées par l'API France Travail
        2. désactivation des offres en base qui ne sont plus dans la collecte API -> is_active = False
        3. filtrage des offres déjà existantes en base
        4. enregistrement des nouvelles offres en base
        Args:
            params: paramètres de recherche (ex: codeROME, localisation, etc.)
            page_size: taille de page API
            max_offres: nombre max d'offres à collecter
        Returns:
            Liste d'offres d'emploi (dictionnaires bruts)
        """
        self.logger.info("Début de la collecte des offres", params=params, page_size=page_size, max_offres=max_offres)
        try:
            jobs = self._fetch_jobs_from_api(params, page_size, max_offres)
            existing_jobs = await self.job_repo.get_all_active_source_id()
            await self._deactivate_missing_jobs(jobs, existing_jobs)
            jobs = self._filter_existing_jobs(jobs, existing_jobs)
            await self._save_new_jobs(jobs)
        except Exception as e:
            self.logger.error("[CollectJobsService] Erreur lors de la collecte des offres", error=str(e), params=params)
            raise

        self.logger.info("[CollectJobsService] Exécution du pipeline de traitement des offres", nb_offres=len(jobs))
        marked_jobs = self.pipeline.run_pipeline(jobs)
        self.logger.info("[CollectJobsService] Pipeline terminé", nb_offres=len(marked_jobs))
        return marked_jobs

    def _fetch_jobs_from_api(self, params: Dict[str, Any], page_size: int, max_offres: int | None) -> List[Job]:
        jobs_raw = self.job_client.collect_offres_paginated(params, page_size=page_size, max_offres=max_offres)
        self.logger.info("[CollectJobsService] Collecte terminée nombre d'offres = ", nb_offres=len(jobs_raw))
        jobs = []
        for job_data in jobs_raw:
            # Ajout du champ source explicite si absent
            print(self.job_client.SOURCE)
            if 'source' not in job_data or job_data['source'] is None:
                job_data['source'] = getattr(self.job_client, 'SOURCE', 'unknown')
            try:
                jobs.append(Job.from_api(job_data))
            except Exception as e:
                self.logger.warning("[CollectJobsService] Offre ignorée (erreur parsing)", error=str(e), job_data=job_data)
        return jobs

    async def _deactivate_missing_jobs(self, jobs: List[Job], existing_jobs: List[str]) -> None:
        api_source_ids = set(job.source_id for job in jobs)
        to_deactivate = [source_id for source_id in existing_jobs if source_id not in api_source_ids and source_id is not None]
        if to_deactivate:
            self.logger.info("[CollectJobsService] Désactivation des offres absentes de la collecte API", nb_offres=len(to_deactivate))
            await self.job_repo.deactivate_jobs_by_source_ids(to_deactivate)
            self.logger.info("[CollectJobsService] Offres désactivées", nb_offres=len(to_deactivate))

    def _filter_existing_jobs(self, jobs: List[Job], existing_jobs: List[str]) -> List[Job]:
        self.logger.info("[CollectJobsService] récupération des offres déjà en BDD", nb_offres=len(existing_jobs))
        filtered = [job for job in jobs if job.source_id not in existing_jobs]
        self.logger.info("[CollectJobsService] Filtrage des offres déjà en BDD", nb_offres=len(existing_jobs))
        self.logger.info("[CollectJobsService] début de l'enregistrement des offres filtrées", nb_offres=len(filtered))
        return filtered

    async def _save_new_jobs(self, jobs: List[Job]) -> None:
        # On convertit chaque Job en dict pour l'insertion MongoDB
        jobs_dicts = [job.to_dict() for job in jobs]
        await self.job_repo.save_jobs(jobs_dicts)
        self.logger.info("[CollectJobsService] enregistrement des offres filtrées terminé", nb_offres=len(jobs))
