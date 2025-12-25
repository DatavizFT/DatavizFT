"""
Base Data Collector - Classe abstraite pour collecteurs multi-sources
Interface commune pour tous les collecteurs de données d'offres d'emploi
"""

from abc import ABC, abstractmethod
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ...database.repositories import OffresRepository
from ...tools.logging_config import get_logger

logger = get_logger(__name__)


class BaseDataCollector(ABC):
    """
    Classe abstraite pour les collecteurs de données
    Définit l'interface commune pour toutes les sources d'offres d'emploi
    """

    def __init__(self, source_name: str, config: dict[str, Any] | None = None):
        """
        Initialise le collecteur de base

        Args:
            source_name: Nom de la source (ex: "france_travail", "adzuna", "jooble")
            config: Configuration spécifique à la source
        """
        self.source_name = source_name
        self.config = config or {}

        # Repositories (à initialiser via set_database)
        self.offres_repo: OffresRepository | None = None

        logger.info(f"Collecteur {self.source_name} initialisé")

    def set_database(self, db: AsyncIOMotorDatabase):
        """
        Configure l'accès à la base de données

        Args:
            db: Instance de base MongoDB
        """
        self.offres_repo = OffresRepository(db)
        logger.debug(f"Base de données configurée pour {self.source_name}")

    @abstractmethod
    async def collect_raw_jobs(
        self, max_jobs: int | None = None, **kwargs
    ) -> list[dict]:
        """
        Collecte les offres brutes depuis la source externe

        Args:
            max_jobs: Limite du nombre d'offres à collecter
            **kwargs: Parameters spécifiques à chaque source

        Returns:
            Liste des offres brutes (format API source)
        """
        pass

    @abstractmethod
    async def convert_job_to_model(self, raw_job: dict) -> dict:
        """
        Convertit une offre brute en modèle normalisé

        Args:
            raw_job: Offre brute de l'API source

        Returns:
            Modèle d'offre normalisé pour MongoDB
        """
        pass

    @abstractmethod
    def get_job_id(self, raw_job: dict) -> str:
        """
        Extrait l'ID unique de l'offre depuis les données brutes

        Args:
            raw_job: Offre brute de l'API source

        Returns:
            ID unique de l'offre
        """
        pass

    async def get_collection_stats(self) -> dict[str, Any]:
        """
        Obtient les statistiques de collecte pour cette source

        Returns:
            Statistiques de la source
        """
        if not self.offres_repo:
            return {"error": "Base de données non configurée"}

        try:
            # Compter les offres de cette source
            total_offres = await self.offres_repo.collection.count_documents(
                {"source": self.source_name}
            )

            # Dernière collecte
            derniere_collecte = await self.offres_repo.collection.find_one(
                {"source": self.source_name}, sort=[("date_collecte", -1)]
            )

            return {
                "source": self.source_name,
                "nb_offres_total": total_offres,
                "derniere_collecte": (
                    derniere_collecte.get("date_collecte")
                    if derniere_collecte
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Erreur stats {self.source_name}: {e}")
            return {"source": self.source_name, "error": str(e)}
