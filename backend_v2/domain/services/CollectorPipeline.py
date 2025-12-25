"""
CollectorPipeline - Orchestrateur des étapes métier pour la collecte et le traitement des offres d'emploi
Permet d'appliquer des transformations, enrichissements et analyses en mode séquentiel ou parallèle
"""

from typing import Callable, List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from backend_v2.shared import logger


# --- Étape de pipeline : marquer les nouvelles offres ---
def mark_new_jobs_step(existing_ids: set):
    """
    Retourne une fonction qui marque chaque job comme nouveau ou non.
    Args:
        existing_ids: set des identifiants déjà présents en BDD
    Returns:
        Fonction à utiliser dans le pipeline
    """
    def step(job: Dict[str, Any]) -> Dict[str, Any]:
        job_id = job.get('id') or job.get('source_id')
        job['is_new'] = job_id not in existing_ids
        return job
    return step

class CollectorPipeline:
    def __init__(self, steps: Optional[List[Callable[[Dict[str, Any]], Dict[str, Any]]]] = None, parallel: bool = False, max_workers: int = 4):
        """
        Args:
            steps: Liste de fonctions à appliquer à chaque offre (job)
            parallel: Exécution parallèle des étapes sur chaque offre
            max_workers: Nombre de threads pour le mode parallèle
        """
        self.steps = steps or []
        self.parallel = parallel
        self.max_workers = max_workers
        self.logger = logger.bind(pipeline="CollectorPipeline")
        self.logger.info("Initialisation du pipeline de collecte", parallel=parallel, max_workers=max_workers)

    def add_step(self, step: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.logger.info("Ajout d'une étape au pipeline", step=str(step))
        self.steps.append(step)

    def run_pipeline(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applique le pipeline sur la liste d'offres.
        """
        self.logger.info("Exécution du pipeline sur les jobs", nb_jobs=len(jobs), nb_steps=len(self.steps))
        if not self.steps:
            self.logger.info("Aucune étape à exécuter dans le pipeline")
            return jobs
        try:
            if self.parallel:
                self.logger.info("Exécution en mode parallèle")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    result = list(executor.map(self._process_job, jobs))
            else:
                self.logger.info("Exécution en mode séquentiel")
                result = [self._process_job(job) for job in jobs]
            self.logger.info("Pipeline exécuté avec succès", nb_jobs=len(result))
            return result
        except Exception as e:
            self.logger.error("Erreur lors de l'exécution du pipeline", error=str(e))
            raise

    def _process_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        for idx, step in enumerate(self.steps):
            self.logger.info("Application d'une étape du pipeline", step_index=idx)
            job = step(job)
        return job

# --- Exemple d'utilisation ---
# Supposons que tu as récupéré la liste des jobs via l'API et la liste des ids existants via le repository
# jobs = [...]  # Liste de jobs récupérés
# existing_ids = set([...])  # Set d'identifiants existants
# pipeline = CollectorPipeline()
# pipeline.add_step(mark_new_jobs_step(existing_ids))
# jobs_annotated = pipeline.run_pipeline(jobs)
