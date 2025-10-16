#!/usr/bin/env python3
"""
Test simplifié du pipeline MongoDB
Version directe sans imports complexes
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le backend au path Python
sys.path.append(str(Path(__file__).parent.parent))

from backend.config import Config
from backend.database import close_database, get_database, init_database
from backend.database.repositories import (
    CompetencesRepository,
    OffresRepository,
    StatsRepository,
)
from backend.tools.logging_config import get_logger

logger = get_logger(__name__)


class TestSimplePipeline:
    """Test simplifié du pipeline"""

    def __init__(self):
        """Initialise le test"""
        self.config = Config()
        self.db = None
        self.offres_repo = None
        self.competences_repo = None
        self.stats_repo = None

    async def init_components(self) -> bool:
        """Initialise les composants"""
        try:
            # MongoDB
            success = await init_database()
            if not success:
                return False

            self.db = get_database()
            self.offres_repo = OffresRepository(self.db)
            self.competences_repo = CompetencesRepository(self.db)
            self.stats_repo = StatsRepository(self.db)

            logger.info("✅ Composants initialisés")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur init: {e}")
            return False

    async def test_repositories(self) -> bool:
        """Test des repositories"""
        logger.info("🔧 Test des repositories")

        try:
            # Test offres
            stats_offres = await self.offres_repo.get_collection_stats()
            logger.info(f"📊 Statistiques offres: {stats_offres}")

            # Test compétences
            nb_competences = await self.competences_repo.count_competences()
            logger.info(f"🧠 Compétences en base: {nb_competences}")

            # Test de création d'une offre basique
            offre_test = {
                "source_id": f"test_{datetime.now().timestamp()}",
                "intitule": "Développeur Test MongoDB",
                "description": "Offre de test pour MongoDB",
                "date_creation": datetime.now(),
                "date_collecte": datetime.now(),
                "entreprise": {"nom": "Test Corp"},
                "localisation": {
                    "ville": "Paris",
                    "code_postal": "75001",
                    "departement": "75"
                },
                "contrat": {"type": "CDI"},
                "competences_extraites": [],
                "code_rome": "M1805",
                "source": "test_pipeline",
                "traite": False
            }

            # Insérer l'offre test
            result = await self.db.offres.insert_one(offre_test)
            logger.info(f"✅ Offre test insérée: {result.inserted_id}")

            # Lire l'offre
            offre_lue = await self.db.offres.find_one({"_id": result.inserted_id})
            if offre_lue:
                logger.info(f"✅ Offre lue: {offre_lue['intitule']}")

            # Nettoyer
            await self.db.offres.delete_one({"_id": result.inserted_id})
            logger.info("🗑️ Offre test supprimée")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur test repositories: {e}")
            return False

    async def test_competences_operations(self) -> bool:
        """Test des opérations sur les compétences"""
        logger.info("🧠 Test opérations compétences")

        try:
            # Lister les compétences existantes
            competences_existantes = await self.competences_repo.get_all_competences_names()
            logger.info(f"📋 Compétences existantes: {len(competences_existantes)}")

            # Créer une compétence test
            competence_test = {
                "nom": "Test MongoDB Pipeline",
                "nom_normalise": "test mongodb pipeline",
                "categorie": "technique",
                "synonymes": ["test mongo", "test pipeline"],
                "description": "Compétence de test pour le pipeline",
                "niveau_demande": "confirme",
                "frequence_detection": 1,
                "derniere_detection": datetime.now(),
            }

            result = await self.db.competences.insert_one(competence_test)
            logger.info(f"✅ Compétence test créée: {result.inserted_id}")

            # Test recherche
            competence_trouvee = await self.competences_repo.find_competence_by_name("Test MongoDB Pipeline")
            if competence_trouvee:
                logger.info(f"✅ Compétence trouvée par nom: {competence_trouvee['nom']}")

            # Nettoyer
            await self.db.competences.delete_one({"_id": result.inserted_id})
            logger.info("🗑️ Compétence test supprimée")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur test compétences: {e}")
            return False

    async def test_stats_generation(self) -> bool:
        """Test génération de statistiques"""
        logger.info("📊 Test génération statistiques")

        try:
            # Générer des statistiques de base
            stats = {
                "periode_analysee": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "date_analyse": datetime.now(),
                "nb_offres_analysees": 0,
                "source": "test_pipeline",
                "top_competences": [],
                "stats_par_departement": {},
                "stats_par_type_contrat": {},
            }

            # Sauvegarder
            result = await self.db.stats_competences.insert_one(stats)
            logger.info(f"✅ Statistiques test sauvegardées: {result.inserted_id}")

            # Lire les statistiques récentes
            stats_recentes = await self.stats_repo.get_latest_stats()
            if stats_recentes:
                logger.info(f"📈 Dernières stats: {stats_recentes.get('periode_analysee')}")

            # Nettoyer
            await self.db.stats_competences.delete_one({"_id": result.inserted_id})
            logger.info("🗑️ Statistiques test supprimées")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur test stats: {e}")
            return False

    async def run_all_tests(self) -> dict:
        """Exécute tous les tests"""
        logger.info("🧪 DÉBUT TESTS PIPELINE SIMPLIFIÉ")
        start_time = datetime.now()

        results = {
            "success": False,
            "tests_passed": 0,
            "tests_total": 0,
            "errors": [],
        }

        try:
            if not await self.init_components():
                results["errors"].append("Échec initialisation")
                return results

            tests = [
                ("repositories", self.test_repositories),
                ("competences", self.test_competences_operations),
                ("stats", self.test_stats_generation),
            ]

            results["tests_total"] = len(tests)

            for name, test_func in tests:
                logger.info(f"🔍 Test: {name}")
                try:
                    if await test_func():
                        results["tests_passed"] += 1
                        logger.info(f"✅ {name} réussi")
                    else:
                        results["errors"].append(f"{name}: échec")
                        logger.error(f"❌ {name} échoué")
                except Exception as e:
                    results["errors"].append(f"{name}: {str(e)}")
                    logger.error(f"❌ {name}: {e}")

            results["success"] = results["tests_passed"] == results["tests_total"]

            duree = datetime.now() - start_time
            logger.info(f"🎯 Tests terminés en {duree}")
            logger.info(f"   Réussis: {results['tests_passed']}/{results['tests_total']}")

            if results["success"]:
                logger.info("🎉 TOUS LES TESTS RÉUSSIS")
            else:
                logger.warning(f"⚠️ Erreurs: {', '.join(results['errors'])}")

            return results

        except Exception as e:
            results["errors"].append(f"Erreur globale: {str(e)}")
            logger.error(f"❌ Erreur globale: {e}")
            return results

        finally:
            try:
                await close_database()
                logger.info("🔌 MongoDB fermé")
            except Exception as e:
                logger.warning(f"Erreur fermeture: {e}")


async def main():
    """Fonction principale"""
    print("🧪 Test Pipeline MongoDB Simplifié - DatavizFT")
    print("=" * 55)

    tester = TestSimplePipeline()
    results = await tester.run_all_tests()

    print("\n" + "="*50)
    print("📋 RÉSULTATS TESTS")
    print("="*50)

    if results["success"]:
        print("✅ SUCCÈS - Pipeline MongoDB opérationnel")
    else:
        print("❌ ÉCHECS DÉTECTÉS")
        for error in results["errors"]:
            print(f"   • {error}")

    print(f"Tests réussis: {results['tests_passed']}/{results['tests_total']}")

    return results["success"]


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
