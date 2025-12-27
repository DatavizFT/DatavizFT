"""
Script pour corriger le champ source dans les offres MongoDB
Détecte la source depuis l'URL de l'offre ou l'origine
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_v2.infrastructure.database.mongodb import MongoDBConnection


async def main():
    """Corriger le champ source pour toutes les offres"""
    print("=" * 80)
    print("CORRECTION DU CHAMP SOURCE - DatavizFT")
    print("=" * 80)

    mongo_conn = MongoDBConnection()
    db = mongo_conn.async_db

    try:
        await db.command("ping")
        print("[OK] Connexion MongoDB établie\n")

        # Compter les offres
        total_offres = await db.offres.count_documents({})
        offres_sans_source = await db.offres.count_documents({
            "$or": [
                {"source": {"$exists": False}},
                {"source": None},
            ]
        })

        print(f"📊 État actuel:")
        print(f"  Total offres: {total_offres}")
        print(f"  Offres sans source: {offres_sans_source}\n")

        if offres_sans_source == 0:
            print("✅ Toutes les offres ont déjà un champ source!")
            return

        print(f"🔧 Correction de {offres_sans_source} offres...\n")

        # Récupérer toutes les offres sans source
        cursor = db.offres.find({
            "$or": [
                {"source": {"$exists": False}},
                {"source": None},
            ]
        })

        nb_france_travail = 0
        nb_adzuna = 0
        nb_inconnu = 0

        async for offre in cursor:
            offre_id = offre["_id"]
            url_offre = offre.get("url_offre", "")
            origine = offre.get("origine")

            # Déterminer la source
            source = None

            # Méthode 1: depuis l'URL
            if "francetravail.fr" in url_offre or "pole-emploi.fr" in url_offre:
                source = "francetravail"
            elif "adzuna" in url_offre:
                source = "adzuna"

            # Méthode 2: depuis le champ origine
            if not source and origine == 1:  # Origine 1 = France Travail
                source = "francetravail"
            elif not source and origine == 2:  # Origine 2 = Adzuna (hypothèse)
                source = "adzuna"

            # Méthode 3: valeur par défaut
            if not source:
                source = "francetravail"  # Par défaut France Travail
                nb_inconnu += 1

            # Mise à jour
            await db.offres.update_one(
                {"_id": offre_id},
                {"$set": {"source": source}}
            )

            if source == "francetravail":
                nb_france_travail += 1
            elif source == "adzuna":
                nb_adzuna += 1

        print("=" * 80)
        print("📈 RÉSULTATS")
        print("=" * 80)
        print(f"✅ Correction terminée!")
        print(f"   • France Travail: {nb_france_travail} offres")
        print(f"   • Adzuna: {nb_adzuna} offres")
        print(f"   • Source inconnue (défaut France Travail): {nb_inconnu} offres")
        print("=" * 80)

        # Vérifier l'état final
        offres_sans_source_final = await db.offres.count_documents({
            "$or": [
                {"source": {"$exists": False}},
                {"source": None},
            ]
        })
        print(f"\n📊 Offres restantes sans source: {offres_sans_source_final}")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if mongo_conn._async_client:
            mongo_conn._async_client.close()
            print("\n[OK] Connexion MongoDB fermée")


if __name__ == "__main__":
    asyncio.run(main())
