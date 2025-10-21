"""
JobRepository - Port d'accès aux offres d'emploi pour le domaine
Définit l'interface attendue par le domaine, à implémenter côté infrastructure
"""
from typing import List, Protocol, Any

class JobRepository(Protocol):
    async def get_all_job_ids(self) -> List[Any]:
        """
        Retourne la liste des identifiants de toutes les offres en base.
        """
        ...

    async def save_jobs(self, jobs: List[dict]) -> None:
        """
        Enregistre une liste d'offres d'emploi en base.
        """
        ...

    async def get_job_by_id(self, job_id: Any) -> dict | None:
        """
        Récupère une offre par son identifiant.
        """
        ...

    async def get_all_active_source_id(self) -> List[Any]:
        """
        Retourne la liste de tous les source_id des offres actives en base.
        """
        ...

    async def get_all_jobs_source_id(self) -> List[Any]:
        """
        Retourne la liste de tous les source_id présents en base.
        """
        ...
