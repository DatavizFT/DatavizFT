#!/usr/bin/env python3
"""
Script de test du pipeline MongoDB
Tests unitaires et d'intégration du nouveau pipeline
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le backend au path Python
sys.path.append(str(Path(__file__).parent.parent))

from backend.clients.france_travail import FranceTravailAPIClient
from backend.config import Config
from backend.database import close_database, get_database, init_database
from backend.pipelines.france_travail_mongodb import PipelineMongoDBM1805
from backend.tools.logging_config import get_logger

logger = get_logger(__name__)


class TesteurPipelineMongoDB:
    """Testeur pour le pipeline MongoDB"""

    def __init__(self):
        """Initialise le testeur"""
        self.config = Config()
        self.pipeline = None
        self.client_api = None

    async def setup(self) -> bool:
        """Setup des composants de test"""
        try:
            # Initialiser MongoDB
            success = await init_database()
            if not success:
                logger.error("Échec initialisation MongoDB")
                return False

            # Créer le client API
            self.client_api = FranceTravailAPIClient()

            # Créer le pipeline
            self.pipeline = PipelineMongoDBM1805(config=self.config)

            logger.info("✅ Setup des composants terminé")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur setup: {e}")
            return False

    async def teardown(self):
        """Nettoyage après tests"""
        try:
            if self.client_api:
                await self.client_api.close()
            await close_database()
            logger.info("Nettoyage terminé")
        except Exception as e:
            logger.warning(f"Erreur nettoyage: {e}")

    async def test_connexion_mongodb(self) -> bool:
        """Test de connexion MongoDB"""
        logger.info("🔗 Test connexion MongoDB")

        try:
            db = get_database()

            # Test ping
            await db.command("ping")

            # Test collections
            collections = await db.list_collection_names()
            collections_requises = ["offres", "competences", "competences_detections"]

            for collection in collections_requises:
                if collection not in collections:
                    logger.error(f"Collection manquante: {collection}")
                    return False

            logger.info("✅ Connexion MongoDB OK")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            return False

    async def test_client_api(self) -> bool:
        """Test du client API France Travail"""
        logger.info("🌐 Test client API France Travail")

        try:
            # Test avec une petite requête
            params = {
                "codeROME": "M1805",
                "range": "0-4",  # Seulement 5 offres
                "departement": "75",  # Paris
            }

            offres = await self.client_api.rechercher_offres(params)

            if not offres:
                logger.warning("Aucune offre retournée par l'API")
                return True  # Pas forcément une erreur

            logger.info(f"✅ API OK - {len(offres)} offres récupérées")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur client API: {e}")
            return False

    async def test_pipeline_complet(self, limite_offres: int = 10) -> bool:
        """Test du pipeline complet avec un petit échantillon"""
        logger.info(f"⚙️ Test pipeline complet (limite: {limite_offres})")

        try:
            start_time = datetime.now()

            # Paramètres de test
            params_recherche = {
                "codeROME": "M1805",
                "range": f"0-{limite_offres-1}",
                "departement": "75",  # Paris pour avoir des résultats
                "typeContrat": "CDI,CDD",
            }

            # Exécuter le pipeline
            resultats = await self.pipeline.executer_pipeline_complet(
                params_recherche=params_recherche,
                analyser_competences=True,
                generer_stats=True
            )

            duree = datetime.now() - start_time

            # Vérifier les résultats
            if not resultats.get("success"):
                logger.error(f"Pipeline échoué: {resultats.get('error')}")
                return False

            stats = resultats.get("resultats", {})
            logger.info(f"✅ Pipeline OK - Durée: {duree}")
            logger.info(f"   Offres collectées: {stats.get('nb_offres_collectees', 0)}")
            logger.info(f"   Offres sauvegardées: {stats.get('nb_offres_sauvegardees', 0)}")
            logger.info(f"   Compétences extraites: {stats.get('nb_competences_extraites', 0)}")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur pipeline complet: {e}")
            return False

    async def test_performance_mongodb(self) -> dict:
        """Test de performance des opérations MongoDB"""
        logger.info("⚡ Test performance MongoDB")

        try:
            db = get_database()

            # Test insertion
            start_time = datetime.now()
            test_doc = {
                "test_id": "performance_test",
                "timestamp": datetime.now(),
                "data": "test performance" * 100
            }

            await db.test_performance.insert_one(test_doc)
            duree_insert = datetime.now() - start_time

            # Test lecture
            start_time = datetime.now()
            doc = await db.test_performance.find_one({"test_id": "performance_test"})
            duree_read = datetime.now() - start_time

            # Test suppression
            await db.test_performance.delete_one({"test_id": "performance_test"})

            perf = {
                "insertion_ms": duree_insert.total_seconds() * 1000,
                "lecture_ms": duree_read.total_seconds() * 1000,
            }

            logger.info(f"✅ Performance - Insert: {perf['insertion_ms']:.1f}ms, Read: {perf['lecture_ms']:.1f}ms")
            return perf

        except Exception as e:
            logger.error(f"❌ Erreur test performance: {e}")
            return {}

    async def test_statistiques_base(self) -> bool:
        """Test des statistiques de base MongoDB"""
        logger.info("📊 Test statistiques de base")

        try:
            db = get_database()

            # Compter les documents dans chaque collection
            stats = {}
            collections = ["offres", "competences", "competences_detections", "stats_competences"]

            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                stats[collection_name] = count

            logger.info("📈 Statistiques collections:")
            for collection, count in stats.items():
                logger.info(f"   {collection}: {count:,} documents")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur statistiques: {e}")
            return False

    async def executer_tests_complets(self, limite_offres: int = 10) -> dict:
        """Exécute tous les tests"""
        logger.info("🧪 DÉBUT TESTS PIPELINE MONGODB")
        start_time = datetime.now()

        resultats = {
            "success": False,
            "tests": {},
            "duree_totale": None,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Setup
            if not await self.setup():
                resultats["error"] = "Échec setup"
                return resultats

            # Tests individuels
            tests = [
                ("connexion_mongodb", self.test_connexion_mongodb),
                ("client_api", self.test_client_api),
                ("performance_mongodb", self.test_performance_mongodb),
                ("statistiques_base", self.test_statistiques_base),
                ("pipeline_complet", lambda: self.test_pipeline_complet(limite_offres)),
            ]

            for nom_test, fonction_test in tests:
                logger.info(f"🔍 Exécution test: {nom_test}")
                try:
                    resultat = await fonction_test()
                    resultats["tests"][nom_test] = {
                        "success": bool(resultat),
                        "resultat": resultat
                    }
                except Exception as e:
                    resultats["tests"][nom_test] = {
                        "success": False,
                        "error": str(e)
                    }

            # Évaluer le succès global
            tous_reussis = all(test["success"] for test in resultats["tests"].values())
            resultats["success"] = tous_reussis

            duree = datetime.now() - start_time
            resultats["duree_totale"] = str(duree)

            if tous_reussis:
                logger.info(f"🎉 TOUS LES TESTS RÉUSSIS - Durée: {duree}")
            else:
                echecs = [nom for nom, test in resultats["tests"].items() if not test["success"]]
                logger.warning(f"⚠️ Tests échoués: {', '.join(echecs)}")

            return resultats

        except Exception as e:
            logger.error(f"❌ Erreur globale tests: {e}")
            resultats["error"] = str(e)
            return resultats

        finally:
            await self.teardown()


def afficher_resultats_tests(resultats: dict):
    """Affiche les résultats des tests de façon lisible"""
    print("\n" + "="*70)
    print("🧪 RÉSULTATS TESTS PIPELINE MONGODB")
    print("="*70)

    if resultats.get("success"):
        print("✅ TOUS LES TESTS RÉUSSIS")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        if "error" in resultats:
            print(f"Erreur globale: {resultats['error']}")

    print(f"\nDurée totale: {resultats.get('duree_totale', 'N/A')}")

    print("\n📋 Détail des tests:")
    for nom_test, resultat_test in resultats.get("tests", {}).items():
        status = "✅" if resultat_test["success"] else "❌"
        print(f"  {status} {nom_test}")

        if not resultat_test["success"] and "error" in resultat_test:
            print(f"     Erreur: {resultat_test['error']}")
        elif resultat_test.get("resultat") and isinstance(resultat_test["resultat"], dict):
            # Afficher des détails si disponibles
            for key, value in resultat_test["resultat"].items():
                if isinstance(value, (int, float)) and key.endswith("_ms"):
                    print(f"     {key}: {value:.1f}ms")


async def main():
    """Fonction principale"""
    print("🧪 Tests du Pipeline MongoDB - DatavizFT")
    print("=" * 50)

    import argparse
    parser = argparse.ArgumentParser(description="Tests pipeline MongoDB")
    parser.add_argument("--limite", type=int, default=10, help="Limite d'offres pour le test complet")
    parser.add_argument("--quick", action="store_true", help="Tests rapides sans pipeline complet")

    args = parser.parse_args()

    testeur = TesteurPipelineMongoDB()

    if args.quick:
        print("⚡ Mode tests rapides (sans pipeline complet)")
        # Tests sans pipeline complet
        resultats = {"tests": {}, "success": True}

        if await testeur.setup():
            tests_rapides = [
                ("connexion_mongodb", testeur.test_connexion_mongodb),
                ("performance_mongodb", testeur.test_performance_mongodb),
                ("statistiques_base", testeur.test_statistiques_base),
            ]

            for nom, fonction in tests_rapides:
                try:
                    resultat = await fonction()
                    resultats["tests"][nom] = {"success": bool(resultat)}
                except Exception as e:
                    resultats["tests"][nom] = {"success": False, "error": str(e)}

            await testeur.teardown()
        else:
            resultats["success"] = False
    else:
        resultats = await testeur.executer_tests_complets(args.limite)

    afficher_resultats_tests(resultats)

    return resultats.get("success", False)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
