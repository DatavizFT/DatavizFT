#!/usr/bin/env python3
"""
Script de vérification des données complètes en MongoDB
Utilise la même configuration que le pipeline principal
"""

import asyncio
import json
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.database.mongodb_connector import MongoDBConnector


async def verifier_donnees_completes():
    """Vérifie qu'une offre MongoDB contient toutes les données API"""

    # Utiliser le même connecteur que le pipeline
    connector = MongoDBConnector()

    try:
        # Connexion avec les mêmes paramètres
        db = await connector.get_database()
        collection = db.offres_emploi

        # Récupérer une offre récente
        offres = await collection.find({}).sort([("date_collecte", -1)]).limit(1).to_list(length=1)

        if not offres:
            print("❌ Aucune offre trouvée en base")
            return

        offre = offres[0]
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

            # Exemple complet de la première offre
            print("\n📋 EXEMPLE COMPLET D'OFFRE API:")
            print("=" * 60)
            print(json.dumps(donnees_api, ensure_ascii=False, indent=2)[:2000] + "...")

        else:
            print("❌ DONNÉES API COMPLÈTES MANQUANTES")
            print("🔍 Champs disponibles dans l'offre:")
            for key in sorted(offre.keys()):
                if key != "_id":
                    print(f"   - {key}")

        # Vérification des nouveaux champs du modèle étendu
        nouveaux_champs = [
            "donnees_api_originales", "rome_code", "rome_libelle", "appellation_libelle",
            "code_naf", "secteur_activite_libelle", "qualification_code", "qualification_libelle",
            "formations", "langues", "permis", "competences_requises", "contact", "agence",
            "nombre_postes", "accessible_th", "tranche_effectif_etab", "origine_offre", "contexte_travail"
        ]

        print("\n🆕 VÉRIFICATION DES NOUVEAUX CHAMPS ÉTENDUS:")
        for champ in nouveaux_champs:
            if champ in offre:
                valeur = offre[champ]
                if isinstance(valeur, (dict, list)):
                    print(f"   ✅ {champ}: {type(valeur).__name__} avec {len(valeur) if valeur else 0} éléments")
                else:
                    preview = str(valeur)[:50] + "..." if len(str(valeur)) > 50 else str(valeur)
                    print(f"   ✅ {champ}: {preview}")
            else:
                print(f"   ❌ {champ}: MANQUANT")

        print(f"\n📊 TAILLE TOTALE DE L'OFFRE: {len(json.dumps(offre, default=str))} caractères")

    finally:
        await connector.close()


if __name__ == "__main__":
    asyncio.run(verifier_donnees_completes())
