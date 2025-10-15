"""
DatavizFT - Point d'entrée principal
Exécute le pipeline de collecte et d'analyse des offres M1805
"""

import os
import sys

# Ajouter le dossier parent au path pour les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipelines.france_travail_m1805 import run_pipelineFT
from backend.tools.logging_config import configure_logging, get_logger


def main_force():
    """Point d'entrée pour forcer l'exécution (ignore la vérification 24h)"""
    configure_logging()
    logger = get_logger(__name__)
    
    logger.warning("Démarrage forcé du pipeline (ignore la vérification 24h)", 
                  extra={"mode": "force", "component": "main"})

    try:
        # Exécuter le pipeline en forçant
        resultat = run_pipelineFT(forcer_execution=True)

        if resultat["success"]:
            logger.success("Pipeline forcé exécuté avec succès", 
                          extra={
                              "pipeline": "france_travail_m1805", 
                              "mode": "force", 
                              "status": "success",
                              "nb_offres": resultat['nb_offres']
                          })
            logger.info(f"{resultat['nb_offres']} offres M1805 collectées et analysées", 
                       extra={"component": "data_collection", "count": resultat['nb_offres']})
            logger.info("Fichiers générés dans le dossier data/", 
                       extra={"component": "file_output", "location": "data/"})
        else:
            logger.error("Erreur lors de l'exécution du pipeline", 
                        extra={
                            "pipeline": "france_travail_m1805", 
                            "mode": "force", 
                            "status": "failed",
                            "error": resultat['error']
                        })

    except Exception as e:
        logger.critical("Erreur fatale lors de l'exécution", 
                       extra={"error": str(e), "mode": "force", "component": "main"},
                       exc_info=True)


def main():
    """Point d'entrée principal - Lance le pipeline complet"""
    configure_logging()
    logger = get_logger(__name__)
    
    logger.info("Démarrage du pipeline DatavizFT", 
               extra={"mode": "normal", "component": "main"})

    try:
        # Exécuter le pipeline complet avec vérification automatique
        resultat = run_pipelineFT()

        if resultat["success"]:
            if resultat.get("skipped"):
                logger.info("Pipeline ignoré - exécution récente détectée", 
                           extra={
                               "pipeline": "france_travail_m1805", 
                               "mode": "normal", 
                               "status": "skipped",
                               "nb_offres": resultat.get('nb_offres', 'N/A')
                           })
                logger.info(f"Dernière collecte: {resultat.get('nb_offres', 'N/A')} offres", 
                           extra={"component": "cache_check", "count": resultat.get('nb_offres', 'N/A')})
                if resultat.get("dernier_fichier"):
                    import os
                    logger.info(f"Fichier existant: {os.path.basename(resultat['dernier_fichier'])}", 
                               extra={"component": "file_check", "filename": os.path.basename(resultat['dernier_fichier'])})
            else:
                logger.success("Pipeline exécuté avec succès", 
                              extra={
                                  "pipeline": "france_travail_m1805", 
                                  "mode": "normal", 
                                  "status": "success",
                                  "nb_offres": resultat['nb_offres']
                              })
                logger.info(f"{resultat['nb_offres']} offres M1805 collectées et analysées", 
                           extra={"component": "data_collection", "count": resultat['nb_offres']})
                logger.info("Fichiers générés dans le dossier data/", 
                           extra={"component": "file_output", "location": "data/"})
        else:
            logger.error("Erreur lors de l'exécution du pipeline", 
                        extra={
                            "pipeline": "france_travail_m1805", 
                            "mode": "normal", 
                            "status": "failed",
                            "error": resultat['error']
                        })

    except Exception as e:
        logger.critical("Erreur fatale lors de l'exécution", 
                       extra={"error": str(e), "mode": "normal", "component": "main"},
                       exc_info=True)


if __name__ == "__main__":
    # Vérifier les arguments pour le forçage
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        main_force()
    else:
        main()
