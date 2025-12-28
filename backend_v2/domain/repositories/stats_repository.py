"""
StatsRepository - Port d'accès aux statistiques pour le domaine
Définit l'interface attendue par le domaine, à implémenter côté infrastructure
"""
from typing import List, Protocol, Any, Optional


class StatsRepository(Protocol):
    """Interface pour l'accès aux statistiques et analyses"""

    async def save_competence_stats(self, stats: dict) -> bool:
        """
        Sauvegarde les statistiques de compétences.

        Args:
            stats: Dictionnaire de statistiques à sauvegarder

        Returns:
            True si sauvegarde réussie
        """
        ...

    async def get_latest_stats(self) -> Optional[dict]:
        """
        Récupère les dernières statistiques disponibles.

        Returns:
            Document des dernières statistiques
        """
        ...

    async def get_stats_by_periode(self, periode: str) -> Optional[dict]:
        """
        Récupère les statistiques d'une période spécifique.

        Args:
            periode: Période au format "YYYY-MM" ou "YYYY-QN"

        Returns:
            Statistiques de la période ou None
        """
        ...

    async def get_evolution_competence(
        self, competence: str, nb_periodes: int = 12
    ) -> List[dict]:
        """
        Récupère l'évolution d'une compétence sur plusieurs périodes.

        Args:
            competence: Nom de la compétence
            nb_periodes: Nombre de périodes à récupérer

        Returns:
            Liste des points d'évolution
        """
        ...

    async def calculate_realtime_stats(self, jours: int = 30) -> dict:
        """
        Calcule des statistiques temps réel sur les N derniers jours.

        Args:
            jours: Nombre de jours à analyser

        Returns:
            Statistiques temps réel
        """
        ...

    async def get_tendances_competences(
        self, seuil_croissance: float = 0.1
    ) -> dict:
        """
        Identifie les tendances d'évolution des compétences.

        Args:
            seuil_croissance: Seuil pour détecter croissance/déclin

        Returns:
            Dict avec listes de compétences croissantes/déclinantes/stables
        """
        ...

    async def get_stats_geographiques(
        self, competence: Optional[str] = None
    ) -> dict:
        """
        Calcule les statistiques géographiques.

        Args:
            competence: Compétence spécifique (optionnel)

        Returns:
            Statistiques par région/département
        """
        ...

    async def cleanup_old_stats(self, nb_periodes_a_garder: int = 24) -> int:
        """
        Nettoie les anciennes statistiques.

        Args:
            nb_periodes_a_garder: Nombre de périodes à conserver

        Returns:
            Nombre de documents supprimés
        """
        ...
