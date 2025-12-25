#!/usr/bin/env python3
"""
Script simple de vérification des données MongoDB
Utilise directement Motor avec les mêmes paramètres
"""

import asyncio
import json
import os

from motor.motor_asyncio import AsyncIOMotorClient


async def verifier_donnees():
    """Vérifie une offre MongoDB"""

    # Configuration MongoDB (même que le pipeline)
    MONGO_URL = os.getenv(
        "MONGODB_URL",
        "mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin"
    )
    MONGO_DB = os.getenv("MONGODB_DATABASE", "dataviz_ft_dev")

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db.offres

    try:
        # Compter les offres
        count = await collection.count_documents({})
        print(f"📊 Nombre total d'offres en base: {count}")

        # Récupérer une offre récente
        offre = await collection.find_one(
            {},
            sort=[("date_collecte", -1)]
        )

        if not offre:
            print("❌ Aucune offre trouvée")
            return

        print(f"\n🔍 Offre ID: {offre.get('source_id', 'N/A')}")
        print(f"📝 Titre: {offre.get('intitule', 'N/A')}")

        # Lister tous les champs disponibles
        print(f"\n📋 CHAMPS DISPONIBLES ({len(offre)} champs):")
        for key in sorted(offre.keys()):
            if key != "_id":
                valeur = offre[key]
                if isinstance(valeur, dict):
                    print(f"   📁 {key}: dict avec {len(valeur)} clés")
                elif isinstance(valeur, list):
                    print(f"   📝 {key}: list avec {len(valeur)} éléments")
                else:
                    preview = str(valeur)[:60] + "..." if len(str(valeur)) > 60 else str(valeur)
                    print(f"   📄 {key}: {preview}")

        # Vérifier spécifiquement donnees_api_originales
        if "donnees_api_originales" in offre:
            api_data = offre["donnees_api_originales"]
            print("\n🎯 DONNÉES API ORIGINALES TROUVÉES!")
            print(f"   📊 {len(api_data)} champs API conservés")

            # Lister quelques champs API clés
            champs_api = ["id", "intitule", "entreprise", "lieuTravail", "salaire", "contact", "formations", "competences"]
            print("\n   🔍 Vérification des champs API clés:")
            for champ in champs_api:
                if champ in api_data:
                    print(f"      ✅ {champ}: présent")
                else:
                    print(f"      ❌ {champ}: manquant")

            # Exemple du lieu de travail avec coordonnées GPS
            if "lieuTravail" in api_data:
                lieu = api_data["lieuTravail"]
                print("\n   📍 LIEU DE TRAVAIL (exemple GPS):")
                for k, v in lieu.items():
                    print(f"      - {k}: {v}")

        else:
            print("\n❌ DONNÉES API ORIGINALES MANQUANTES!")

        print(f"\n📏 Taille de l'offre: {len(json.dumps(offre, default=str))} caractères")

    except Exception as e:
        print(f"❌ Erreur: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(verifier_donnees())
