#!/usr/bin/env python3
"""
Analyse des données de localisation manquantes dans MongoDB
"""

import asyncio

from backend.database import get_database


async def analyser_donnees_manquantes():
    """Analyse les données de localisation manquantes dans MongoDB"""

    try:
        db = get_database()
        collection = db.offres

        # Statistiques globales
        total_offres = await collection.count_documents({})
        print(f"Total d'offres en base: {total_offres}")

        # Offres avec coordonnées GPS
        with_coordinates = await collection.count_documents({
            "localisation.latitude": {"$exists": True, "$ne": None},
            "localisation.longitude": {"$exists": True, "$ne": None}
        })
        print(f"Offres avec coordonnees GPS: {with_coordinates}")

        # Offres sans coordonnées
        without_coordinates = total_offres - with_coordinates
        print(f"Offres sans coordonnees: {without_coordinates}")

        # Échantillon d'une offre actuelle
        sample = await collection.find_one({})
        if sample:
            print("\nStructure localisation actuelle:")
            localisation = sample.get("localisation", {})
            for key, value in localisation.items():
                print(f"  {key}: {value}")

        if total_offres > 0:
            print(f"\nTaux de couverture GPS: {(with_coordinates/total_offres)*100:.1f}%")

    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(analyser_donnees_manquantes())
