#!/usr/bin/env python3
"""
Nettoyage des collections MongoDB avant migration
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import motor.motor_asyncio

from backend.config import Config


async def clean():
    client = motor.motor_asyncio.AsyncIOMotorClient(Config().MONGODB_URL)
    db = client[Config().MONGODB_DATABASE]

    result = await db.offres.delete_many({})
    print(f'Offres supprimées: {result.deleted_count}')

    result = await db.competences_detections.delete_many({})
    print(f'Détections supprimées: {result.deleted_count}')

    client.close()

asyncio.run(clean())
