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

from backend.pipelines.france_travail_m1805 import (
    run_pipelineFT,
    run_pipeline_avec_limite,
    PipelineM1805,
)
from backend.tools.logging_config import configure_logging, get_logger


def afficher_statistiques():
    """Affiche les statistiques du pipeline avec logging structuré"""
    configure_logging()
    logger = get_logger(__name__)
    
    logger.info("Récupération des statistiques du pipeline", 
               extra={"component": "stats", "pipeline": "M1805"})
    
    try:
        pipeline = PipelineM1805()
        stats = pipeline.obtenir_statistiques_pipeline()
        
        logger.info("Statistiques du pipeline M1805", extra={
            "code_rome": stats['code_rome'],
            "nb_categories_competences": stats['nb_categories_competences'],
            "nb_competences_total": stats['nb_competences_total'],
            "stockage": stats['stockage'],
            "component": "stats"
        })
        
        # Affichage formaté pour l'utilisateur
        print("📊 STATISTIQUES PIPELINE M1805")
        print("=" * 50)
        print(f"Code ROME: {stats['code_rome']}")
        print(f"Catégories de compétences: {stats['nb_categories_competences']}")
        print(f"Compétences totales: {stats['nb_competences_total']}")
        print(f"Stockage: {stats['stockage']}")
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des statistiques", 
                    extra={"error": str(e), "component": "stats"},
                    exc_info=True)
        print(f"❌ Erreur statistiques: {e}")


def main_avec_limite(limite: int):
    """Exécute le pipeline avec une limite d'offres"""
    configure_logging()
    logger = get_logger(__name__)
    
    logger.warning("Exécution du pipeline avec limite", 
                  extra={"limite": limite, "component": "main", "mode": "limit"})

    try:
        resultat = run_pipeline_avec_limite(limite)

        if resultat["success"]:
            logger.success("Pipeline avec limite exécuté avec succès", 
                          extra={
                              "pipeline": "france_travail_m1805",
                              "mode": "limit",
                              "limite": limite,
                              "status": "success",
                              "nb_offres": resultat['nb_offres']
                          })
            logger.info(f"{resultat['nb_offres']} offres collectées (limite: {limite})", 
                       extra={"component": "data_collection", "count": resultat['nb_offres'], "limite": limite})
        else:
            logger.error("Erreur lors de l'exécution du pipeline avec limite", 
                        extra={
                            "pipeline": "france_travail_m1805",
                            "mode": "limit",
                            "limite": limite,
                            "status": "failed",
                            "error": resultat['error']
                        })

    except Exception as e:
        logger.critical("Erreur fatale lors de l'exécution avec limite", 
                       extra={"error": str(e), "mode": "limit", "limite": limite, "component": "main"},
                       exc_info=True)


def main_force():
    """Point d'entrée pour forcer l'exécution (ignore la vérification 24h)"""
    configure_logging()
    logger = get_logger(__name__)

    logger.warning(
        "Démarrage forcé du pipeline (ignore la vérification 24h)",
        extra={"mode": "force", "component": "main"},
    )

    try:
        # Exécuter le pipeline en forçant
        resultat = run_pipelineFT(forcer_execution=True)

        if resultat["success"]:
            logger.success(
                "Pipeline forcé exécuté avec succès",
                extra={
                    "pipeline": "france_travail_m1805",
                    "mode": "force",
                    "status": "success",
                    "nb_offres": resultat["nb_offres"],
                },
            )
            logger.info(
                f"{resultat['nb_offres']} offres M1805 collectées et analysées",
                extra={"component": "data_collection", "count": resultat["nb_offres"]},
            )
            logger.info(
                "Fichiers générés dans le dossier data/",
                extra={"component": "file_output", "location": "data/"},
            )
        else:
            logger.error(
                "Erreur lors de l'exécution du pipeline",
                extra={
                    "pipeline": "france_travail_m1805",
                    "mode": "force",
                    "status": "failed",
                    "error": resultat["error"],
                },
            )

    except Exception as e:
        logger.critical(
            "Erreur fatale lors de l'exécution",
            extra={"error": str(e), "mode": "force", "component": "main"},
            exc_info=True,
        )


def main():
    """Point d'entrée principal - Lance le pipeline complet"""
    configure_logging()
    logger = get_logger(__name__)

    logger.info(
        "Démarrage du pipeline DatavizFT", extra={"mode": "normal", "component": "main"}
    )

    try:
        # Exécuter le pipeline complet avec vérification automatique
        resultat = run_pipelineFT()

        if resultat["success"]:
            if resultat.get("skipped"):
                logger.info(
                    "Pipeline ignoré - exécution récente détectée",
                    extra={
                        "pipeline": "france_travail_m1805",
                        "mode": "normal",
                        "status": "skipped",
                        "nb_offres": resultat.get("nb_offres", "N/A"),
                    },
                )
                logger.info(
                    f"Dernière collecte: {resultat.get('nb_offres', 'N/A')} offres",
                    extra={
                        "component": "cache_check",
                        "count": resultat.get("nb_offres", "N/A"),
                    },
                )
                if resultat.get("dernier_fichier"):
                    import os

                    logger.info(
                        f"Fichier existant: {os.path.basename(resultat['dernier_fichier'])}",
                        extra={
                            "component": "file_check",
                            "filename": os.path.basename(resultat["dernier_fichier"]),
                        },
                    )
            else:
                logger.success(
                    "Pipeline exécuté avec succès",
                    extra={
                        "pipeline": "france_travail_m1805",
                        "mode": "normal",
                        "status": "success",
                        "nb_offres": resultat["nb_offres"],
                    },
                )
                logger.info(
                    f"{resultat['nb_offres']} offres M1805 collectées et analysées",
                    extra={
                        "component": "data_collection",
                        "count": resultat["nb_offres"],
                    },
                )
                logger.info(
                    "Fichiers générés dans le dossier data/",
                    extra={"component": "file_output", "location": "data/"},
                )
        else:
            logger.error(
                "Erreur lors de l'exécution du pipeline",
                extra={
                    "pipeline": "france_travail_m1805",
                    "mode": "normal",
                    "status": "failed",
                    "error": resultat["error"],
                },
            )

    except Exception as e:
        logger.critical(
            "Erreur fatale lors de l'exécution",
            extra={"error": str(e), "mode": "normal", "component": "main"},
            exc_info=True,
        )


def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Pipeline DatavizFT M1805 - Collecte et analyse des offres d\'emploi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples d'utilisation:
  python backend/main.py                 # Exécution normale
  python backend/main.py --force         # Forcer l'exécution
  python backend/main.py --limit 50      # Limiter à 50 offres
  python backend/main.py --stats         # Afficher les statistiques
        '''
    )
    
    parser.add_argument(
        '--force', 
        action='store_true', 
        help='Forcer l\'exécution (ignore la vérification 24h)'
    )
    
    parser.add_argument(
        '--limit', 
        type=int, 
        help='Limiter le nombre d\'offres collectées'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true', 
        help='Afficher les statistiques du pipeline'
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    if args.stats:
        afficher_statistiques()
    elif args.limit:
        main_avec_limite(args.limit)
    elif args.force:
        main_force()
    else:
        main()
