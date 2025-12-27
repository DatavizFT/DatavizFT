"""
Script pour normaliser le champ source dans MongoDB
Convertir "France_Travail" → "francetravail"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_v2.infrastructure.database.mongodb import MongoDBConnection


async def main():
    """Normaliser le champ source"""
    print("=" * 80)
    print("NORMALISATION DU CHAMP SOURCE - DatavizFT")
    print("=" * 80)

    mongo_conn = MongoDBConnection()
    db = mongo_conn.async_db

    try:
        await db.command("ping")
        print("[OK] Connexion MongoDB établie\n")

        # État actuel
        print("Repartition AVANT normalisation:")
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        async for doc in db.offres.aggregate(pipeline):
            print(f"   {doc['_id']}: {doc['count']} offres")

        # Normaliser "France_Travail" → "francetravail"
        result1 = await db.offres.update_many(
            {"source": "France_Travail"},
            {"$set": {"source": "francetravail"}}
        )

        # Normaliser "Adzuna" → "adzuna" (au cas où)
        result2 = await db.offres.update_many(
            {"source": "Adzuna"},
            {"$set": {"source": "adzuna"}}
        )

        print(f"\nNormalisation effectuee:")
        print(f"   France_Travail -> francetravail: {result1.modified_count} offres")
        print(f"   Adzuna -> adzuna: {result2.modified_count} offres")

        # État final
        print("\nRepartition APRES normalisation:")
        async for doc in db.offres.aggregate(pipeline):
            print(f"   {doc['_id']}: {doc['count']} offres")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if mongo_conn._async_client:
            mongo_conn._async_client.close()
            print("\n[OK] Connexion MongoDB fermée")


if __name__ == "__main__":
    asyncio.run(main())
