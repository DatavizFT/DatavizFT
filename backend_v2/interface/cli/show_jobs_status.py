"""
Script CLI pour afficher les offres actives et inactives en base MongoDB
Usage : python -m backend_v2.interface.cli.show_jobs_status
"""

import asyncio
import json
from bson import ObjectId
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.infrastructure.repositories.job_repository_mongodb import JobRepositoryMongoDB
from backend_v2.shared import logger

class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

async def main():
    mongo = MongoDBConnection()
    job_repo = JobRepositoryMongoDB(mongo.async_db)

    logger.info("[CLI] Récupération des offres actives...")
    actives = await mongo.async_db["offres"].find({"is_active": True}).to_list(length=None)
    logger.info(f"[CLI] {len(actives)} offres actives trouvées.")

    logger.info("[CLI] Récupération des offres inactives...")
    inactives = await mongo.async_db["offres"].find({"is_active": False}).to_list(length=None)
    logger.info(f"[CLI] {len(inactives)} offres inactives trouvées.")

    print("\n--- OFFRES ACTIVES ---")
    print(json.dumps(actives, cls=MongoJsonEncoder, ensure_ascii=False, indent=2))
    print("\n--- OFFRES INACTIVES ---")
    print(json.dumps(inactives, cls=MongoJsonEncoder, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
