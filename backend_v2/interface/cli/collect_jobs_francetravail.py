"""
Script CLI pour tester l'appel à l'API France Travail
Usage : python -m backend_v2.interface.cli.collect_jobs_francetravail
"""



import sys
import asyncio
import json
from bson import ObjectId
from backend_v2.infrastructure.clients import FranceTravailAPIClient
from backend_v2.infrastructure.clients.adzuna_api import AdzunaAPIClient
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
    import argparse
    parser = argparse.ArgumentParser(description="Collecte d'offres d'emploi depuis différentes sources")
    parser.add_argument("--source", choices=["francetravail", "adzuna"], default="francetravail", help="Source d'offres à collecter")
    parser.add_argument("--code_rome", type=str, default="M1805", help="Code ROME pour la recherche (France Travail)")
    parser.add_argument("--query", type=str, default=None, help="Recherche texte (Adzuna)")
    args = parser.parse_args()

    logger.info(f"[CLI] Démarrage de la collecte des offres", source=args.source, code_rome=args.code_rome, query=args.query)

    try:
        if args.source == "francetravail":
            client = FranceTravailAPIClient()
            params = {"codeROME": args.code_rome}
        else:
            client = AdzunaAPIClient()
            params = {"what": args.query or "", "results_per_page": 150}

        mongo = MongoDBConnection()
        job_repo = JobRepositoryMongoDB(mongo.async_db)
        service = CollectJobsService(client, job_repo)
        logger.info("[CLI] Lancement de la collecte via CollectJobsService")
        total_offre = await service.collect_jobs(params, page_size=150)

    except DatavizFTException as e:
        logger.error("[CLI] Erreur métier DatavizFT", error=str(e), details=getattr(e, 'job_data', None))
    except Exception as e:
        logger.error("[CLI] Erreur inattendue", error=str(e), exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
