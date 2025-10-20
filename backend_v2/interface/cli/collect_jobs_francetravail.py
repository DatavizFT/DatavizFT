"""
Script CLI pour tester l'appel à l'API France Travail
Usage : python -m backend_v2.interface.cli.collect_jobs_francetravail
"""



import sys
import asyncio
import json
from bson import ObjectId
from backend_v2.infrastructure.external_apis import FranceTravailAPIClient
from backend_v2.application.services.collect_jobs_service import CollectJobsService
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.infrastructure.repositories.job_repository_mongodb import JobRepositoryMongoDB
from backend_v2.shared import logger, DatavizFTException
class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)



async def main():
    code_rome = sys.argv[1] if len(sys.argv) > 1 else "M1805"
    logger.info("[CLI] Démarrage de la collecte des offres France Travail", code_rome=code_rome)

    try:
        client = FranceTravailAPIClient()
        service = CollectJobsService(client)
        logger.info("[CLI] Lancement de la collecte via CollectJobsService")
        total_offre = service.collect_jobs({"codeROME": code_rome}, page_size=150, max_offres=100)

        # Connexion MongoDB et repository
        mongo = MongoDBConnection()
        job_repo = JobRepositoryMongoDB(mongo.async_db)

        # recuperation de tous les ids en base
        logger.info("[CLI] Récupération des source_id en base MongoDB")
        job_id = await job_repo.get_all_jobs_source_id()
        logger.info("[CLI] Nombre d'id en base MongoDB", nb_id=len(job_id))
        if job_id:
            logger.info("[CLI] Premier id en base MongoDB", first_id=job_id[0])
        # if total_offre:
        #     logger.info("Première offre brute (JSON):\n" + json.dumps(total_offre[0], indent=2, ensure_ascii=False, cls=MongoJsonEncoder))

    except DatavizFTException as e:
        logger.error("[CLI] Erreur métier DatavizFT", error=str(e), details=getattr(e, 'job_data', None))
    except Exception as e:
        logger.error("[CLI] Erreur inattendue", error=str(e), exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
