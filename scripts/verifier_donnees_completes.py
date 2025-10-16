#!/usr/bin/env python3
"""
Script de vérification des données complètes en MongoDB
Vérifie qu'une offre contient toutes les données de l'API France Travail
"""

import asyncio
import json

from motor.motor_asyncio import AsyncIOMotorClient


async def verifier_donnees_completes():
    """Vérifie qu'une offre MongoDB contient toutes les données API"""

    # Connexion MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.dataviz_ft
    collection = db.offres_emploi

    try:
        # Récupérer une offre récente
        offre = await collection.find_one(
            {},
            sort=[("date_collecte", -1)]
        )

        if not offre:
            print("❌ Aucune offre trouvée en base")
            return

        print(f"🔍 Analyse de l'offre ID: {offre.get('source_id', 'N/A')}")
        print(f"📝 Intitulé: {offre.get('intitule', 'N/A')}")
        print(f"📅 Date collecte: {offre.get('date_collecte', 'N/A')}")
        print()

        # Vérifier la présence du champ donnees_api_originales
        if "donnees_api_originales" in offre:
            donnees_api = offre["donnees_api_originales"]
            print("✅ DONNÉES API COMPLÈTES PRÉSENTES")
            print(f"🗃️  Nombre de champs API: {len(donnees_api)}")

            # Afficher les champs principaux
            champs_principaux = [
                "id", "intitule", "description", "dateCreation", "dateActualisation",
                "lieuTravail", "romeCode", "romeLibelle", "entreprise", "typeContrat",
                "experienceExige", "formations", "langues", "permis", "competences",
                "salaire", "contact", "agence", "nombrePostes", "accessibleTH",
                "secteurActivite", "qualificationCode", "origineOffre", "contexteTravail"
            ]

            print("\n📋 VÉRIFICATION DES CHAMPS CLÉS:")
            for champ in champs_principaux:
                if champ in donnees_api:
                    valeur = donnees_api[champ]
                    if isinstance(valeur, (dict, list)):
                        print(f"   ✅ {champ}: {type(valeur).__name__} avec {len(valeur)} éléments")
                    else:
                        preview = str(valeur)[:50] + "..." if len(str(valeur)) > 50 else str(valeur)
                        print(f"   ✅ {champ}: {preview}")
                else:
                    print(f"   ❌ {champ}: MANQUANT")

            # Vérifier les sous-objets complexes
            print("\n🏢 ENTREPRISE:")
            entreprise = donnees_api.get("entreprise", {})
            if entreprise:
                for key, value in entreprise.items():
                    print(f"   - {key}: {value}")
            else:
                print("   ❌ Pas d'informations entreprise")

            print("\n📍 LIEU DE TRAVAIL:")
            lieu = donnees_api.get("lieuTravail", {})
            if lieu:
                for key, value in lieu.items():
                    print(f"   - {key}: {value}")
            else:
                print("   ❌ Pas d'informations de lieu")

            print("\n💰 SALAIRE:")
            salaire = donnees_api.get("salaire", {})
            if salaire:
                for key, value in salaire.items():
                    print(f"   - {key}: {value}")
            else:
                print("   ❌ Pas d'informations salariales")

            print("\n📞 CONTACT:")
            contact = donnees_api.get("contact", {})
            if contact:
                for key, value in contact.items():
                    print(f"   - {key}: {value}")
            else:
                print("   ❌ Pas d'informations de contact")

            print("\n🎓 FORMATIONS:")
            formations = donnees_api.get("formations", [])
            if formations:
                for i, formation in enumerate(formations):
                    print(f"   Formation {i+1}:")
                    for key, value in formation.items():
                        print(f"     - {key}: {value}")
            else:
                print("   ❌ Pas de formations requises")

            print("\n💼 COMPÉTENCES:")
            competences = donnees_api.get("competences", [])
            if competences:
                for i, comp in enumerate(competences):
                    print(f"   Compétence {i+1}:")
                    for key, value in comp.items():
                        print(f"     - {key}: {value}")
            else:
                print("   ❌ Pas de compétences spécifiées")

        else:
            print("❌ DONNÉES API COMPLÈTES MANQUANTES")
            print("🔍 Champs disponibles dans l'offre:")
            for key in sorted(offre.keys()):
                if key != "_id":
                    print(f"   - {key}")

        print(f"\n📊 TAILLE TOTALE DE L'OFFRE: {len(json.dumps(offre, default=str))} caractères")

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(verifier_donnees_completes())
