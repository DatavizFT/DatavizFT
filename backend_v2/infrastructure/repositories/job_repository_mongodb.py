"""
Implémentation MongoDB du JobRepository pour l'infrastructure
"""
from typing import List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend_v2.domain.repositories.job_repository import JobRepository

class JobRepositoryMongoDB:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "offres"):
        from backend_v2.shared import logger
        self.db = db
        self.collection = db[collection_name]
        self.logger = logger.bind(repository="JobRepositoryMongoDB", collection=collection_name)
        self.logger.info("Initialisation du repository MongoDB", collection=collection_name)

    async def get_all_job_ids(self) -> List[Any]:
        """
        Retourne la liste des identifiants de toutes les offres en base.
        """
        self.logger.info("Récupération de tous les job_ids depuis MongoDB")
        try:
            cursor = self.collection.find({}, {"_id": 0, "id": 1})
            ids = [doc.get("id") for doc in await cursor.to_list(length=None)]
            self.logger.info("Récupération job_ids terminée", nb_ids=len(ids))
            return ids
        except Exception as e:
            self.logger.error("Erreur lors de la récupération des job_ids", error=str(e))
            raise

    async def save_jobs(self, jobs: List[dict]) -> None:
        """
        Enregistre une liste d'offres d'emploi en base (insert many, ignore duplicates).
        """
        if not jobs:
            self.logger.info("Aucun job à enregistrer, skip insert_many.")
            return
        try:
            result = await self.collection.insert_many(jobs, ordered=False)
            self.logger.info("Jobs insérés en base MongoDB", nb_jobs=len(result.inserted_ids))
        except Exception as e:
            self.logger.error("Erreur lors de l'insertion des jobs", error=str(e), nb_jobs=len(jobs))
            raise

    async def get_job_by_id(self, job_id: Any) -> dict | None:
        """
        Récupère une offre par son identifiant.
        """
        self.logger.info("Recherche d'un job par id", job_id=job_id)
        try:
            job = await self.collection.find_one({"id": job_id})
            found = job is not None
            self.logger.info("Résultat de la recherche job_id", job_id=job_id, found=found)
            return job
        except Exception as e:
            self.logger.error("Erreur lors de la recherche du job par id", error=str(e), job_id=job_id)
            raise
    
    async def get_all_jobs_source_id(self) -> List[Any]:
        """
        Retourne la liste de tous les source_id présents en base.
        """
        self.logger.info("Récupération de tous les source_id depuis MongoDB")
        try:
            cursor = self.collection.find({}, {"_id": 0, "source_id": 1})
            source_ids = [doc.get("source_id") for doc in await cursor.to_list(length=None)]
            self.logger.info("Récupération source_id terminée", nb_source_ids=len(source_ids))
            return source_ids
        except Exception as e:
            self.logger.error("Erreur lors de la récupération des source_id", error=str(e))
            raise
