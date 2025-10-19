"""
Script CLI pour tester l'appel à l'API France Travail
Usage : python -m backend_v2.interface.cli.collect_jobs_francetravail
"""


from backend_v2.infrastructure.external_apis import FranceTravailAPIClient
from backend_v2.application.services.collect_jobs_service import CollectJobsService
from backend_v2.shared import logger, DatavizFTException
import sys


def main():
    # Exemple : collecte des offres pour le code ROME M1805 (Informatique)
    code_rome = sys.argv[1] if len(sys.argv) > 1 else "M1805"

    logger.info(f"Collecte des offres France Travail pour le code ROME : {code_rome}")

    try:
        client = FranceTravailAPIClient()
        service = CollectJobsService(client)
        offres = service.collect_jobs({"codeROME": code_rome}, page_size=10, max_offres=10)
        total_offre = service.collect_jobs({"codeROME": "M1805"}, page_size=150, max_offres=None)
        logger.info(f"Nombre d'offres collectées : {len(offres)}")
        for i, offre in enumerate(offres, 1):
            logger.info(
                f"Offre {i} : {offre.get('intitule', 'Sans titre')}",
                extra={
                    "id": offre.get('id') or offre.get('idOffre'),
                    "description": (offre.get('description', '')[:120] + '...') if offre.get('description') else '',
                }
            )
        logger.info(f"Nombre total d'offres disponibles pour {code_rome} : {len(total_offre)}")
    except DatavizFTException as e:
        logger.error(f"Erreur métier DatavizFT : {e}", extra={"details": getattr(e, 'job_data', None)})
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}", exc_info=True)

if __name__ == "__main__":
    main()
