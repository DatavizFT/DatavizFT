"""
Implémentation MongoDB du JobRepository pour l'infrastructure
"""

import datetime
from typing import List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend_v2.domain.repositories.job_repository import JobRepository
from backend_v2.shared import logger

class JobRepositoryMongoDB(JobRepository):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "offres"):
        self.db = db
        self.collection = db[collection_name]
        self.logger = logger.bind(repository="JobRepositoryMongoDB", collection=collection_name)
        self.logger.info("[JobRepositoryMongoDB] Initialisation du repository MongoDB", collection=collection_name)

    async def get_all_active_source_id(self) -> List[Any]:
        """
        Retourne la liste de tous les source_id des offres actives en base.
        Une offre est considérée comme active si le champ 'is_active' est True ou absent.
        """
        self.logger.info("[JobRepositoryMongoDB] Récupération des source_id des offres actives depuis MongoDB")
        try:
            # On considère qu'une offre est active si 'is_active' == True ou si le champ n'existe pas
            cursor = self.collection.find({"$or": [{"is_active": True}, {"is_active": {"$exists": False}}]}, {"_id": 0, "source_id": 1})
            active_source_ids = [doc.get("source_id") for doc in await cursor.to_list(length=None)]
            self.logger.info("[JobRepositoryMongoDB] Récupération des source_id actives terminée", nb_active_source_ids=len(active_source_ids))
            return active_source_ids
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de la récupération des source_id actives", error=str(e))
            raise

    async def get_all_job_ids(self) -> List[Any]:
        """
        Retourne la liste des identifiants de toutes les offres en base.
        """
        self.logger.info("[JobRepositoryMongoDB] Récupération de tous les job_ids depuis MongoDB")
        try:
            cursor = self.collection.find({}, {"_id": 0, "id": 1})
            ids = [doc.get("id") for doc in await cursor.to_list(length=None)]
            self.logger.info("[JobRepositoryMongoDB] Récupération job_ids terminée", nb_ids=len(ids))
            return ids
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de la récupération des job_ids", error=str(e))
            raise

    async def save_jobs(self, jobs: List[dict]) -> None:
        """
        Enregistre une liste d'offres d'emploi en base (insert many, ignore duplicates).
        """
        if not jobs:
            self.logger.info("[JobRepositoryMongoDB] Aucun job à enregistrer, skip insert_many.")
            return
        try:
            #ajout du champs is_active à True par défaut, de la date d'insertion, date de traitement, is_traited
            for job in jobs:
                job['is_active'] = True
                job['date_insertion'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                job['date_traitement'] = None
                job['is_traited'] = False

            result = await self.collection.insert_many(jobs, ordered=False)
            self.logger.info("[JobRepositoryMongoDB] Jobs insérés en base MongoDB", nb_jobs=len(result.inserted_ids))
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de l'insertion des jobs", error=str(e), nb_jobs=len(jobs))
            raise

    async def get_job_by_id(self, job_id: Any) -> dict | None:
        """
        Récupère une offre par son identifiant.
        """
        self.logger.info("[JobRepositoryMongoDB] Recherche d'un job par id", job_id=job_id)
        try:
            job = await self.collection.find_one({"id": job_id})
            found = job is not None
            self.logger.info("[JobRepositoryMongoDB] Résultat de la recherche job_id", job_id=job_id, found=found)
            return job
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de la recherche du job par id", error=str(e), job_id=job_id)
            raise
    
    async def get_all_jobs_source_id(self) -> List[Any]:
        """
        Retourne la liste de tous les source_id présents en base.
        """
        self.logger.info("[JobRepositoryMongoDB] Récupération de tous les source_id depuis MongoDB")
        try:
            cursor = self.collection.find({}, {"_id": 0, "source_id": 1})
            source_ids = [doc.get("source_id") for doc in await cursor.to_list(length=None)]
            self.logger.info("[JobRepositoryMongoDB] Récupération source_id terminée", nb_source_ids=len(source_ids))
            return source_ids
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de la récupération des source_id", error=str(e))
            raise

    async def deactivate_jobs_by_source_ids(self, source_ids: List[Any]) -> None:
        """
        Désactive les offres dont le source_id est dans la liste fournie.
        La désactivation se fait en mettant à jour le champ 'is_active' à False.

        Args:
            source_ids: Liste des source_id des offres à désactiver
        """
        if not source_ids:
            self.logger.info("[JobRepositoryMongoDB] Aucun source_id fourni pour la désactivation, skip update.")
            return
        self.logger.info("[JobRepositoryMongoDB] Désactivation des jobs par source_id", nb_source_ids=len(source_ids))
        try:
            result = await self.collection.update_many(
                {"source_id": {"$in": source_ids}},
                {"$set": {"is_active": False}}
            )
            self.logger.info("[JobRepositoryMongoDB] Désactivation des jobs terminée", nb_modified=result.modified_count)
        except Exception as e:
            self.logger.error("[JobRepositoryMongoDB] Erreur lors de la désactivation des jobs", error=str(e))
            raise