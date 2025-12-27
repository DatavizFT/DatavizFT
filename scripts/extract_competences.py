"""
Script pour extraire les compétences des offres MongoDB existantes
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pipelines.base.competence_processor import CompetenceProcessor
from backend_v2.infrastructure.database.mongodb import MongoDBConnection


async def main():
    """Extraction des compétences pour toutes les offres"""
    print("=" * 80)
    print("EXTRACTION DES COMPÉTENCES - DatavizFT")
    print("=" * 80)

    # Connexion MongoDB
    mongo_conn = MongoDBConnection()
    db = mongo_conn.async_db

    try:
        # Vérifier la connexion
        await db.command("ping")
        print("[OK] Connexion MongoDB établie")

        # Compter les offres
        total_offres = await db.offres.count_documents({})
        offres_sans_competences = await db.offres.count_documents({
            "$or": [
                {"competences_extraites": {"$exists": False}},
                {"competences_extraites": []},
            ]
        })

        print(f"\n📊 État actuel:")
        print(f"  Total offres: {total_offres}")
        print(f"  Offres sans compétences extraites: {offres_sans_competences}")

        if offres_sans_competences == 0:
            print("\n✅ Toutes les offres ont déjà des compétences extraites!")
            return

        print(f"\n🚀 Lancement de l'extraction sur {offres_sans_competences} offres...")
        print("   (Cela peut prendre quelques minutes)\n")

        # Importer les dépendances nécessaires
        from backend.tools.competence_analyzer import CompetenceAnalyzer
        from backend.data import COMPETENCES_REFERENTIEL
        from datetime import datetime

        # Créer l'analyzer directement
        analyzer = CompetenceAnalyzer(COMPETENCES_REFERENTIEL)

        # Récupérer les offres sans compétences
        query = {
            "$or": [
                {"competences_extraites": {"$exists": False}},
                {"competences_extraites": []},
            ]
        }
        cursor = db.offres.find(query)
        offres_a_analyser = await cursor.to_list(length=None)

        print(f"📊 {len(offres_a_analyser)} offres à analyser\n")

        # Convertir au format analyzer
        offres_pour_analyse = []
        for offre in offres_a_analyser:
            offres_pour_analyse.append({
                "id": str(offre.get("_id")),
                "source_id": offre.get("source_id"),
                "intitule": offre.get("intitule", ""),
                "description": offre.get("description", ""),
            })

        # Analyse avec CompetenceAnalyzer
        print("🔍 Analyse en cours...")
        resultats_analyse = analyzer.analyser_offres(offres_pour_analyse, verbose=True)

        # Construire le mapping competences_par_offre
        competences_par_offre = {}
        for categorie, data_categorie in resultats_analyse.get("resultats_par_categorie", {}).items():
            competences_detectees = data_categorie.get("competences", [])

            for comp_info in competences_detectees:
                nom_competence = comp_info.get("competence", "")
                offres_avec_competence = comp_info.get("offres", [])

                for offre_info in offres_avec_competence:
                    offre_id = offre_info.get("id", "")
                    if offre_id:
                        if offre_id not in competences_par_offre:
                            competences_par_offre[offre_id] = []

                        if nom_competence not in competences_par_offre[offre_id]:
                            competences_par_offre[offre_id].append(nom_competence)

        print(f"✅ {len(competences_par_offre)} offres avec compétences détectées\n")

        # Mettre à jour les offres dans MongoDB
        nb_mises_a_jour = 0
        for offre in offres_a_analyser:
            offre_id = str(offre.get("_id"))
            competences_liste = competences_par_offre.get(offre_id, [])

            # Mettre à jour même si liste vide (pour marquer comme traité)
            result = await db.offres.update_one(
                {"_id": offre["_id"]},
                {
                    "$set": {
                        "competences_extraites": competences_liste,
                        "traite": True,
                        "date_traitement": datetime.now(),
                    }
                },
            )

            if result.modified_count > 0:
                nb_mises_a_jour += 1

        results = {
            "success": True,
            "nb_offres_analysees": len(offres_a_analyser),
            "nb_competences_detectees": len(competences_par_offre),
            "nb_offres_mises_a_jour": nb_mises_a_jour,
            "resultats_par_categorie": resultats_analyse.get("resultats_par_categorie", {}),
        }

        print("\n" + "=" * 80)
        print("📈 RÉSULTATS")
        print("=" * 80)

        if results.get("success"):
            print(f"✅ Extraction réussie!")
            print(f"   • Offres analysées: {results.get('nb_offres_analysees', 0)}")
            print(f"   • Offres avec compétences: {results.get('nb_competences_detectees', 0)}")
            print(f"   • Offres mises à jour: {results.get('nb_offres_mises_a_jour', 0)}")
            print(f"   • Détections sauvegardées: {results.get('nb_detections_sauvegardees', 0)}")

            # Afficher les stats par catégorie
            resultats_categorie = results.get('resultats_par_categorie', {})
            if resultats_categorie:
                print("\n📊 Top catégories de compétences détectées:")
                categories_triees = sorted(
                    resultats_categorie.items(),
                    key=lambda x: x[1].get('nb_competences_detectees', 0),
                    reverse=True
                )
                for i, (cat, data) in enumerate(categories_triees[:10], 1):
                    nb_comp = data.get('nb_competences_detectees', 0)
                    print(f"   {i:2d}. {cat}: {nb_comp} compétences")
        else:
            print(f"❌ Erreur lors de l'extraction:")
            print(f"   {results.get('error', 'Erreur inconnue')}")

        # Vérifier l'état final
        print("\n" + "=" * 80)
        offres_avec_competences = await db.offres.count_documents({
            "competences_extraites": {"$exists": True, "$ne": []}
        })
        print(f"📊 État final: {offres_avec_competences}/{total_offres} offres ont des compétences")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Fermer la connexion
        if mongo_conn._async_client:
            mongo_conn._async_client.close()
            print("\n[OK] Connexion MongoDB fermée")


if __name__ == "__main__":
    asyncio.run(main())
