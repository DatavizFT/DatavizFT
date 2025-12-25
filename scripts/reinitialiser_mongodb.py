#!/usr/bin/env python3
"""
Script de réinitialisation MongoDB pour tester la structure complète
Vide les collections et re-collecte avec la nouvelle structure
"""

import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient


async def reinitialiser_mongodb():
    """Vide les collections MongoDB pour permettre une re-collecte complète"""

    # Configuration MongoDB
    MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGODB_DB_NAME", "dataviz_ft")
    MONGO_USER = os.getenv("MONGODB_USERNAME", "datavizuser")
    MONGO_PASS = os.getenv("MONGODB_PASSWORD", "datavizpass123")

    # URL complète avec authentification
    if MONGO_USER and MONGO_PASS:
        mongo_url = f"mongodb://{MONGO_USER}:{MONGO_PASS}@localhost:27017/{MONGO_DB}"
    else:
        mongo_url = MONGO_URL

    client = AsyncIOMotorClient(mongo_url)
    db = client[MONGO_DB]

    try:
        print("🗄️  RÉINITIALISATION MONGODB POUR STRUCTURE COMPLÈTE")
        print("=" * 60)

        # Compter les données actuelles
        offres_count = await db.offres_emploi.count_documents({})
        competences_count = await db.competences.count_documents({})
        stats_count = await db.statistiques.count_documents({})

        print("📊 Données actuelles:")
        print(f"   - Offres: {offres_count}")
        print(f"   - Compétences: {competences_count}")
        print(f"   - Statistiques: {stats_count}")

        if offres_count == 0:
            print("✅ La base est déjà vide, rien à supprimer")
            return

        # Demander confirmation
        print(f"\n⚠️  ATTENTION: Cette opération va supprimer {offres_count} offres!")
        print("   Cela permettra de re-collecter avec la nouvelle structure complète")
        print("   qui conserve TOUS les champs de l'API France Travail.")

        confirmation = input("\n❓ Voulez-vous continuer? (oui/non): ").lower().strip()

        if confirmation not in ['oui', 'o', 'y', 'yes']:
            print("❌ Opération annulée")
            return

        # Supprimer les collections
        print("\n🗑️  Suppression des collections...")

        # Supprimer les offres
        result_offres = await db.offres_emploi.delete_many({})
        print(f"   ✅ Offres supprimées: {result_offres.deleted_count}")

        # Supprimer les compétences analysées
        result_comp = await db.competences.delete_many({})
        print(f"   ✅ Compétences supprimées: {result_comp.deleted_count}")

        # Supprimer les statistiques
        result_stats = await db.statistiques.delete_many({})
        print(f"   ✅ Statistiques supprimées: {result_stats.deleted_count}")

        # Vérification
        final_count = await db.offres_emploi.count_documents({})
        print("\n✅ RÉINITIALISATION TERMINÉE")
        print(f"   Offres restantes: {final_count}")

        print("\n🚀 PRÊT POUR LA RE-COLLECTE COMPLÈTE")
        print("   Lancez maintenant: python backend/main.py --limit 10")
        print("   Pour tester la conservation complète des données API")

    except Exception as e:
        print(f"❌ Erreur: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(reinitialiser_mongodb())
