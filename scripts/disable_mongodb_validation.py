#!/usr/bin/env python3
"""
Script pour désactiver la validation MongoDB temporairement
Permet la migration avec des champs null
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le backend au path Python
sys.path.append(str(Path(__file__).parent.parent))

import logging

import motor.motor_asyncio

from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def desactiver_validation_mongodb():
    """Désactive la validation MongoDB pour permettre la migration"""
    config = Config()

    # Connexion directe à MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.MONGODB_DATABASE]

    try:
        # Test de connexion
        await client.admin.command('ping')
        logger.info("✅ Connexion MongoDB OK")

        collections = ["offres", "competences", "competences_detections", "stats_competences"]

        for collection_name in collections:
            logger.info(f"🔧 Suppression validation: {collection_name}")

            try:
                # Supprimer la validation
                await db.command('collMod', collection_name, validator={})
                logger.info(f"✅ Validation supprimée pour {collection_name}")

            except Exception as e:
                logger.warning(f"⚠️ Erreur pour {collection_name}: {e}")

        logger.info("🎉 Validation MongoDB supprimée pour migration")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

    finally:
        client.close()
        logger.info("🔌 Connexion MongoDB fermée")


async def main():
    """Fonction principale"""
    print("🔧 Suppression Validation MongoDB - DatavizFT")
    print("=" * 50)

    success = await desactiver_validation_mongodb()

    if success:
        print("\n✅ Validation MongoDB supprimée")
        print("🎯 Vous pouvez maintenant lancer la migration sans erreurs de validation")
    else:
        print("\n❌ Erreur lors de la suppression de la validation")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
