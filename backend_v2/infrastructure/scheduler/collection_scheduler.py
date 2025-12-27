"""
Scheduler pour la collecte automatisée des offres
Lance la collecte toutes les 24h
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from backend_v2.application.services import CollectionService
from backend_v2.shared import logger


class CollectionScheduler:
    """Scheduler pour la collecte automatisée"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.collection_service = CollectionService()
        self.logger = logger.bind(scheduler="CollectionScheduler")

    async def _run_collection(self):
        """Exécuter la collecte automatique"""
        self.logger.info("Démarrage de la collecte automatique planifiée")

        try:
            results = await self.collection_service.collect_all_sources(
                max_offres_per_source=None  # Toutes les offres
            )

            self.logger.info(
                "Collecte automatique terminée",
                nouvelles_offres=results["total_nouvelles_offres"],
                doublons=results["total_doublons"],
                success=results["success"]
            )

        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte automatique: {e}")

    def start(self, run_immediately: bool = False):
        """
        Démarrer le scheduler

        Args:
            run_immediately: Si True, lance une collecte immédiatement au démarrage
        """
        # Planifier la collecte tous les jours à 2h du matin
        self.scheduler.add_job(
            self._run_collection,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_collection",
            name="Collecte quotidienne des offres",
            replace_existing=True,
        )

        self.scheduler.start()
        self.logger.info("Scheduler démarré - Collecte quotidienne à 02:00")

        # Lancer une collecte immédiatement si demandé
        if run_immediately:
            self.logger.info("Lancement d'une collecte immédiate")
            asyncio.create_task(self._run_collection())

    def stop(self):
        """Arrêter le scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler arrêté")

    def get_next_run_time(self) -> datetime | None:
        """Obtenir la prochaine exécution planifiée"""
        job = self.scheduler.get_job("daily_collection")
        if job:
            return job.next_run_time
        return None
