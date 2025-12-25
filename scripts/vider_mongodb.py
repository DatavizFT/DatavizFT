#!/usr/bin/env python3
"""
Script pour vider la base MongoDB et permettre la re-collecte complète
"""

import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient


async def vider_collections_mongodb():
    """Vide les collections MongoDB pour permettre une re-collecte complète"""

    # Configuration MongoDB (même que le pipeline)
    MONGO_URL = os.getenv(
        "MONGODB_URL",
        "mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin"
    )
    MONGO_DB = os.getenv("MONGODB_DATABASE", "dataviz_ft_dev")

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]

    try:
        # Collections à vider
        collections = ["offres", "competences", "stats", "test_datavizft", "test_persistence"]

        for collection_name in collections:
            collection = db[collection_name]

            # Compter avant suppression
            count_avant = await collection.count_documents({})

            if count_avant > 0:
                print(f"🗑️  Suppression de {count_avant} documents dans {collection_name}...")
                result = await collection.delete_many({})
                print(f"   ✅ {result.deleted_count} documents supprimés")
            else:
                print(f"📭 Collection {collection_name} déjà vide")

        print("\n🎯 Base MongoDB vidée ! Prêt pour la re-collecte complète.")
        print("▶️  Exécutez maintenant: python backend/main.py")

    except Exception as e:
        print(f"❌ Erreur: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    print("🚨 ATTENTION: Ce script va SUPPRIMER toutes les données MongoDB !")
    response = input("Continuer ? (oui/non): ").lower().strip()

    if response in ['oui', 'o', 'yes', 'y']:
        asyncio.run(vider_collections_mongodb())
    else:
        print("❌ Annulation - données préservées")
