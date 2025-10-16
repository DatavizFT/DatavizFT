#!/usr/bin/env python3
"""
Script pour nettoyer et recréer les index MongoDB
Résout les conflits d'index
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


async def nettoyer_index_mongodb():
    """Nettoie et recrée les index MongoDB"""
    config = Config()

    # Connexion directe à MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.MONGODB_DATABASE]

    try:
        # Test de connexion
        await client.admin.command('ping')
        logger.info("✅ Connexion MongoDB OK")

        collections_a_nettoyer = ["offres", "competences", "competences_detections", "stats_competences"]

        for collection_name in collections_a_nettoyer:
            collection = db[collection_name]

            logger.info(f"🔧 Nettoyage collection: {collection_name}")

            # Lister les index existants
            try:
                index_info = await collection.list_indexes().to_list(length=None)
                logger.info(f"📋 Index existants dans {collection_name}:")
                for idx in index_info:
                    logger.info(f"   {idx.get('name', 'unnamed')}: {idx.get('key', {})}")

                # Supprimer tous les index sauf _id_
                for idx in index_info:
                    idx_name = idx.get('name', '')
                    if idx_name != '_id_':
                        try:
                            await collection.drop_index(idx_name)
                            logger.info(f"🗑️ Index supprimé: {idx_name}")
                        except Exception as e:
                            logger.warning(f"⚠️ Impossible de supprimer {idx_name}: {e}")

            except Exception as e:
                logger.warning(f"⚠️ Erreur nettoyage {collection_name}: {e}")

        # Recréer les index de base
        logger.info("🔨 Recréation des index de base...")

        # Index pour offres
        try:
            await db.offres.create_index("source_id", unique=True)
            await db.offres.create_index([("date_creation", -1)])
            await db.offres.create_index("competences_extraites")
            logger.info("✅ Index offres créés")
        except Exception as e:
            logger.warning(f"⚠️ Erreur index offres: {e}")

        # Index pour compétences
        try:
            await db.competences.create_index("nom_normalise", unique=True)
            await db.competences.create_index("categorie")
            await db.competences.create_index([("frequence_detection", -1)])
            logger.info("✅ Index compétences créés")
        except Exception as e:
            logger.warning(f"⚠️ Erreur index compétences: {e}")

        # Index pour détections
        try:
            await db.competences_detections.create_index([("offre_id", 1), ("competence", 1)])
            await db.competences_detections.create_index([("date_detection", -1)])
            logger.info("✅ Index détections créés")
        except Exception as e:
            logger.warning(f"⚠️ Erreur index détections: {e}")

        # Index pour stats
        try:
            await db.stats_competences.create_index("periode_analysee")
            await db.stats_competences.create_index([("date_analyse", -1)])
            logger.info("✅ Index stats créés")
        except Exception as e:
            logger.warning(f"⚠️ Erreur index stats: {e}")

        logger.info("🎉 Nettoyage et recréation des index terminés")

        # Vérifier le résultat final
        for collection_name in collections_a_nettoyer:
            collection = db[collection_name]
            try:
                index_info = await collection.list_indexes().to_list(length=None)
                logger.info(f"✅ {collection_name}: {len(index_info)} index finaux")
            except Exception as e:
                logger.warning(f"⚠️ Erreur vérification {collection_name}: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur globale: {e}")
        return False

    finally:
        client.close()
        logger.info("🔌 Connexion MongoDB fermée")


async def main():
    """Fonction principale"""
    print("🔧 Nettoyage Index MongoDB - DatavizFT")
    print("=" * 45)

    success = await nettoyer_index_mongodb()

    if success:
        print("\n✅ Index MongoDB nettoyés et recréés avec succès")
        print("🎯 Vous pouvez maintenant utiliser les pipelines MongoDB")
    else:
        print("\n❌ Erreur lors du nettoyage des index")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
