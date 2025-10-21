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
        mongo = MongoDBConnection()
        job_repo = JobRepositoryMongoDB(mongo.async_db)
        service = CollectJobsService(client, job_repo)
        logger.info("[CLI] Lancement de la collecte via CollectJobsService")
        total_offre = await service.collect_jobs({"codeROME": code_rome}, page_size=150)


    except DatavizFTException as e:
        logger.error("[CLI] Erreur métier DatavizFT", error=str(e), details=getattr(e, 'job_data', None))
    except Exception as e:
        logger.error("[CLI] Erreur inattendue", error=str(e), exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
