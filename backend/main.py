"""
DatavizFT - Point d'entrée principal
Exécute le pipeline de collecte et d'analyse des offres M1805

Usage:
  python backend/main.py                 # Exécution normale (vérification 24h)
  python backend/main.py --force         # Forcer l'exécution
  python backend/main.py --limit 50      # Limiter à 50 offres
  python backend/main.py --stats         # Afficher les statistiques
"""

import argparse
import os
import sys

# Ajouter le dossier parent au path pour les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du nouveau pipeline MongoDB
import asyncio

from backend.pipelines.instances.france_travail_pipeline import FranceTravailPipeline
from backend.tools.logging_config import configure_logging, get_logger


async def afficher_statistiques():
    """Affiche les statistiques du pipeline MongoDB avec logging structuré"""
    configure_logging()
    logger = get_logger(__name__)

    logger.info(
        "Récupération des statistiques du pipeline MongoDB",
        extra={"component": "stats", "pipeline": "M1805_MongoDB"},
    )

    try:
        # Créer le pipeline qui gère sa propre connexion
        pipeline = FranceTravailPipeline()
        stats = await pipeline.obtenir_statistiques_mongodb()

        logger.info(
            "Statistiques du pipeline MongoDB M1805",
            extra={
                "code_rome": stats.get("code_rome", "M1805"),
                "nb_offres_total": stats.get("nb_offres_total", 0),
                "nb_competences_total": stats.get("nb_competences_total", 0),
                "stockage": "MongoDB",
                "component": "stats",
            },
        )

        # Affichage formaté pour l'utilisateur
        print("📊 STATISTIQUES PIPELINE MONGODB M1805")
        print("=" * 55)
        print(f"Code ROME: {stats.get('code_rome', 'M1805')}")
        print(f"Offres en base: {stats.get('nb_offres_total', 0):,}")
        print(f"Compétences uniques: {stats.get('nb_competences_total', 0):,}")
        print(f"Détections: {stats.get('nb_detections_total', 0):,}")
        print("Stockage: MongoDB Atlas/Local")
        print(f"Dernière collecte: {stats.get('derniere_collecte', 'Inconnue')}")

    except Exception as e:
        logger.error(
            "Erreur lors de la récupération des statistiques",
            extra={"error": str(e), "component": "stats"},
            exc_info=True,
        )
        print(f"❌ Erreur statistiques: {e}")
    finally:
        # Fermer la connexion si le pipeline a été créé
        try:
            if "pipeline" in locals():
                await pipeline.close_database_connection()
        except Exception:
            pass


async def main_avec_limite(limite: int):
    """Exécute le pipeline MongoDB avec une limite d'offres"""
    configure_logging()
    logger = get_logger(__name__)

    logger.warning(
        "Exécution du pipeline MongoDB avec limite",
        extra={"limite": limite, "component": "main", "mode": "limit"},
    )

    try:
        pipeline = FranceTravailPipeline()

        # Exécution avec limite
        resultat = await pipeline.executer_pipeline_complet(
            max_offres=limite,
            forcer_execution=True,  # Forcer car on a spécifié une limite
        )

        if resultat["success"]:
            nb_offres = resultat.get("resultats", {}).get("nb_offres_sauvegardees", 0)
            logger.success(
                "Pipeline MongoDB avec limite exécuté avec succès",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "limit",
                    "limite": limite,
                    "status": "success",
                    "nb_offres": nb_offres,
                },
            )
            logger.info(
                f"{nb_offres} offres collectées et sauvegardées (limite: {limite})",
                extra={
                    "component": "data_collection",
                    "count": nb_offres,
                    "limite": limite,
                },
            )
            print(
                f"✅ {nb_offres} offres collectées et sauvegardées en MongoDB (limite: {limite})"
            )
        else:
            error_msg = resultat.get("error", "Erreur inconnue")
            logger.error(
                "Erreur lors de l'exécution du pipeline avec limite",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "limit",
                    "limite": limite,
                    "status": "failed",
                    "error": error_msg,
                },
            )
            print(f"❌ Erreur pipeline: {error_msg}")

    except Exception as e:
        logger.critical(
            "Erreur fatale lors de l'exécution avec limite",
            extra={
                "error": str(e),
                "mode": "limit",
                "limite": limite,
                "component": "main",
            },
            exc_info=True,
        )
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            if "pipeline" in locals():
                await pipeline.close_database_connection()
        except Exception:
            pass


async def main_force():
    """Point d'entrée pour forcer l'exécution complète du pipeline MongoDB"""
    configure_logging()
    logger = get_logger(__name__)

    logger.warning(
        "Démarrage forcé du pipeline MongoDB (collecte complète)",
        extra={"mode": "force", "component": "main"},
    )

    try:
        pipeline = FranceTravailPipeline()

        # Exécuter le pipeline MongoDB complet forcé
        resultat = await pipeline.executer_pipeline_complet(
            max_offres=None, forcer_execution=True  # Aucune limite - toutes les offres API
        )

        if resultat["success"]:
            resultats_details = resultat.get("resultats", {})
            nb_offres = resultats_details.get("nb_offres_sauvegardees", 0)
            nb_competences = resultats_details.get("nb_competences_extraites", 0)

            logger.success(
                "Pipeline MongoDB forcé exécuté avec succès",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "force",
                    "status": "success",
                    "nb_offres": nb_offres,
                    "nb_competences": nb_competences,
                },
            )
            logger.info(
                f"{nb_offres} offres M1805 collectées et sauvegardées en MongoDB",
                extra={"component": "data_collection", "count": nb_offres},
            )
            logger.info(
                f"{nb_competences} compétences extraites et analysées",
                extra={"component": "competence_analysis", "count": nb_competences},
            )
            logger.info(
                "Données sauvegardées dans MongoDB",
                extra={"component": "database_output", "location": "MongoDB"},
            )

            print(
                f"✅ Pipeline forcé terminé: {nb_offres} offres, {nb_competences} compétences"
            )
        else:
            error_msg = resultat.get("error", "Erreur inconnue")
            logger.error(
                "Erreur lors de l'exécution du pipeline forcé",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "force",
                    "status": "failed",
                    "error": error_msg,
                },
            )
            print(f"❌ Erreur pipeline forcé: {error_msg}")

    except Exception as e:
        logger.critical(
            "Erreur fatale lors de l'exécution forcée",
            extra={"error": str(e), "mode": "force", "component": "main"},
            exc_info=True,
        )
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            if "pipeline" in locals():
                await pipeline.close_database_connection()
        except Exception:
            pass


async def main_force_analyses():
    """Forcer l'analyse des compétences et la génération des statistiques"""
    configure_logging()
    logger = get_logger(__name__)

    logger.warning(
        "Démarrage forcé des analyses (compétences + statistiques)",
        extra={"mode": "force_analyses", "component": "main"},
    )

    try:
        pipeline = FranceTravailPipeline()

        # Exécuter le pipeline avec forcer_analyses=True
        resultat = await pipeline.executer_pipeline_complet(
            max_offres=None,  # Aucune limite
            forcer_execution=False,  # Ne pas forcer la collecte
            forcer_analyses=True,  # Forcer les analyses
        )

        if resultat.get("success", False):
            nb_offres = resultat.get("nb_offres_analysees", 0)
            nb_competences = resultat.get("nb_competences_detectees", 0)
            top_competences = resultat.get("top_competences", [])

            logger.info(
                "✅ Analyses forcées terminées avec succès",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "force_analyses",
                    "status": "success",
                    "nb_offres": nb_offres,
                    "nb_competences": nb_competences,
                },
            )

            print(f"📊 Analyses forcées terminées: {nb_offres} offres analysées")
            print(f"🧠 {nb_competences} compétences détectées")

            if top_competences:
                print("🏆 Top 5 compétences:")
                for i, comp in enumerate(top_competences[:5], 1):
                    nom = comp.get("competence", "Unknown")
                    pct = comp.get("pourcentage", 0)
                    print(f"   {i}. {nom}: {pct}%")
        else:
            error_msg = resultat.get("error", "Erreur inconnue")
            logger.error(
                "Erreur lors des analyses forcées",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "force_analyses",
                    "status": "failed",
                    "error": error_msg,
                },
            )
            print(f"❌ Erreur analyses: {error_msg}")

    except Exception as e:
        logger.critical(
            "Erreur fatale lors des analyses forcées",
            extra={"error": str(e), "mode": "force_analyses", "component": "main"},
            exc_info=True,
        )
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            if "pipeline" in locals():
                await pipeline.close_database_connection()
        except Exception:
            pass


async def main():
    """Point d'entrée principal - Lance le pipeline MongoDB avec vérification intelligente"""
    configure_logging()
    logger = get_logger(__name__)

    logger.info(
        "Démarrage du pipeline MongoDB DatavizFT",
        extra={"mode": "normal", "component": "main"},
    )

    try:
        pipeline = FranceTravailPipeline()

        # Vérifier si une collecte récente existe
        derniere_collecte = await pipeline.verifier_collecte_recente()

        if derniere_collecte and not derniere_collecte.get("doit_collecter", True):
            logger.info(
                "Pipeline ignoré - collecte récente détectée en MongoDB",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "normal",
                    "status": "skipped",
                    "derniere_collecte": derniere_collecte.get("date_collecte"),
                    "nb_offres_existantes": derniere_collecte.get("nb_offres", 0),
                },
            )
            print(
                f"⏭️ Collecte récente trouvée: {derniere_collecte.get('nb_offres', 0)} offres"
            )
            print(
                f"   Dernière collecte: {derniere_collecte.get('date_collecte', 'Inconnue')}"
            )
            print("   Utilisez --force pour forcer une nouvelle collecte")
            return

        # Exécuter le pipeline complet avec vérification automatique
        resultat = await pipeline.executer_pipeline_complet(
            max_offres=None,  # Collecte non-modérée par défaut
            forcer_execution=False,  # Respecter la vérification 24h
        )

        if resultat["success"]:
            # Le pipeline retourne directement les données, pas dans une enveloppe "resultats"
            nb_offres = resultat.get("nb_offres_sauvegardees", 0)
            nb_competences = resultat.get("nb_competences_detectees", 0)

            logger.success(
                "Pipeline MongoDB exécuté avec succès",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "normal",
                    "status": "success",
                    "nb_offres": nb_offres,
                    "nb_competences": nb_competences,
                },
            )
            logger.info(
                f"{nb_offres} nouvelles offres M1805 collectées et sauvegardées",
                extra={
                    "component": "data_collection",
                    "count": nb_offres,
                },
            )
            logger.info(
                f"{nb_competences} compétences extraites et analysées",
                extra={"component": "competence_analysis", "count": nb_competences},
            )
            logger.info(
                "Données persistées dans MongoDB",
                extra={"component": "database_output", "location": "MongoDB"},
            )

            print(
                f"✅ Pipeline terminé: {nb_offres} nouvelles offres, {nb_competences} compétences"
            )
            print("📊 Consultez MongoDB pour les données complètes")
        else:
            error_msg = resultat.get("error", "Erreur inconnue")
            logger.error(
                "Erreur lors de l'exécution du pipeline",
                extra={
                    "pipeline": "france_travail_mongodb",
                    "mode": "normal",
                    "status": "failed",
                    "error": error_msg,
                },
            )
            print(f"❌ Erreur pipeline: {error_msg}")

    except Exception as e:
        logger.critical(
            "Erreur fatale lors de l'exécution",
            extra={"error": str(e), "mode": "normal", "component": "main"},
            exc_info=True,
        )
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            if "pipeline" in locals():
                await pipeline.close_database_connection()
        except Exception:
            pass


def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Pipeline DatavizFT M1805 - Collecte et analyse des offres d'emploi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python backend/main.py                 # Exécution normale
  python backend/main.py --force         # Forcer l'exécution complète
  python backend/main.py --force-analyses   # Forcer seulement les analyses
  python backend/main.py --limit 50      # Limiter à 50 offres
  python backend/main.py --stats         # Afficher les statistiques
        """,
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcer l'exécution (ignore la vérification 24h)",
    )

    parser.add_argument(
        "--force-analyses",
        action="store_true",
        help="Forcer l'analyse des compétences et génération des statistiques",
    )

    parser.add_argument(
        "--limit", type=int, help="Limiter le nombre d'offres collectées"
    )

    parser.add_argument(
        "--stats", action="store_true", help="Afficher les statistiques du pipeline"
    )

    return parser.parse_args()


async def run_main():
    """Point d'entrée asynchrone principal"""
    args = parse_arguments()

    if args.stats:
        await afficher_statistiques()
    elif args.force_analyses:
        await main_force_analyses()
    elif args.limit:
        await main_avec_limite(args.limit)
    elif args.force:
        await main_force()
    else:
        await main()


if __name__ == "__main__":
    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)
