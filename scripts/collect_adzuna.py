"""
Script pour collecter des offres d'emploi depuis Adzuna API
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_v2.infrastructure.clients.adzuna_api import AdzunaAPIClient
from backend_v2.infrastructure.database.mongodb import MongoDBConnection
from backend_v2.config import Config


def convert_adzuna_to_db_format(adzuna_offre: dict) -> dict:
    """Convertir une offre Adzuna au format MongoDB"""

    # Extraire la localisation
    location = adzuna_offre.get("location", {})
    location_display = location.get("display_name", "")

    # Créer le document MongoDB
    return {
        "source": "adzuna",
        "source_id": str(adzuna_offre.get("id", "")),
        "intitule": adzuna_offre.get("title", ""),
        "description": adzuna_offre.get("description", ""),
        "date_creation": datetime.fromisoformat(adzuna_offre.get("created").replace("Z", "+00:00")) if adzuna_offre.get("created") else datetime.now(),
        "date_actualisation": None,
        "date_insertion": datetime.now(),
        "url_offre": adzuna_offre.get("redirect_url", ""),
        "type_contrat": adzuna_offre.get("contract_type", "Non spécifié"),
        "type_contrat_libelle": adzuna_offre.get("contract_type", "Non spécifié"),
        "lieu_travail": {
            "libelle": location_display,
            "latitude": location.get("area", [None])[1] if location.get("area") else None,
            "longitude": location.get("area", [None])[0] if location.get("area") else None,
            "codePostal": None,
            "commune": location_display.split(",")[0] if "," in location_display else location_display,
        },
        "entreprise": {
            "nom": adzuna_offre.get("company", {}).get("display_name", ""),
            "entrepriseAdaptee": False,
        },
        "salaire": {
            "libelle": f"{adzuna_offre.get('salary_min', '')} - {adzuna_offre.get('salary_max', '')}" if adzuna_offre.get('salary_min') else None,
            "complement1": None,
            "complement2": None,
        },
        "competences": [],
        "competences_extraites": [],
        "is_active": True,
        "traite": False,
        "origine": 2,  # 1=France Travail, 2=Adzuna
        "raw_data": adzuna_offre,
    }


async def main():
    """Collecter des offres Adzuna et les insérer dans MongoDB"""
    print("=" * 80)
    print("COLLECTE ADZUNA - DatavizFT")
    print("=" * 80)

    # Vérifier les credentials
    if not Config.ADZUNA_APP_ID or not Config.ADZUNA_CLIENT_SECRET:
        print("\nERREUR: Les credentials Adzuna ne sont pas configurés!")
        print("Veuillez définir ADZUNA_APP_ID et ADZUNA_CLIENT_SECRET dans .env")
        return

    print(f"\nConfiguration:")
    print(f"  App ID: {Config.ADZUNA_APP_ID[:10]}...")
    print(f"  App Key: {Config.ADZUNA_CLIENT_SECRET[:10]}...")

    # Connexion MongoDB
    mongo_conn = MongoDBConnection()
    db = mongo_conn.async_db

    try:
        await db.command("ping")
        print("[OK] Connexion MongoDB etablie\n")

        # État actuel
        total_offres = await db.offres.count_documents({})
        adzuna_offres = await db.offres.count_documents({"source": "adzuna"})

        print(f"Etat actuel:")
        print(f"  Total offres: {total_offres}")
        print(f"  Offres Adzuna: {adzuna_offres}\n")

        # Créer le client Adzuna
        client = AdzunaAPIClient()

        # Paramètres de recherche (offres IT en France)
        params = {
            "what": "développeur OR developpeur OR developer OR IT OR informatique",
            "where": "france",
            "content-type": "application/json",
        }

        print("Collecte des offres Adzuna en cours...")
        print("(Cela peut prendre quelques minutes)\n")

        # Collecter max 500 offres
        offres_brutes = client.collect_offres_paginated(
            params=params,
            page_size=50,
            max_offres=500
        )

        print(f"\n{len(offres_brutes)} offres Adzuna recuperees\n")

        if not offres_brutes:
            print("Aucune offre collectee!")
            return

        # Convertir et insérer dans MongoDB
        print("Insertion dans MongoDB...")
        nb_inserted = 0
        nb_duplicates = 0

        for offre_brute in offres_brutes:
            offre_db = convert_adzuna_to_db_format(offre_brute)

            # Vérifier si l'offre existe déjà
            existing = await db.offres.find_one({"source_id": offre_db["source_id"]})

            if existing:
                nb_duplicates += 1
            else:
                await db.offres.insert_one(offre_db)
                nb_inserted += 1

        print(f"\nInsertion terminee:")
        print(f"  Nouvelles offres inserees: {nb_inserted}")
        print(f"  Doublons ignores: {nb_duplicates}")

        # État final
        total_offres_final = await db.offres.count_documents({})
        adzuna_offres_final = await db.offres.count_documents({"source": "adzuna"})

        print(f"\nEtat final:")
        print(f"  Total offres: {total_offres_final}")
        print(f"  Offres Adzuna: {adzuna_offres_final}")

        print("\n" + "=" * 80)
        print("PROCHAINES ETAPES:")
        print("=" * 80)
        print("1. Extraire les competences des nouvelles offres Adzuna:")
        print("   python scripts\\extract_competences.py")
        print("\n2. Rafraichir le dashboard (F5)")
        print("=" * 80)

    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if mongo_conn._async_client:
            mongo_conn._async_client.close()
            print("\n[OK] Connexion MongoDB fermee")


if __name__ == "__main__":
    asyncio.run(main())
