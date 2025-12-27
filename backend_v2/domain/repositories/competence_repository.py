"""
CompetenceRepository - Port d'accès aux compétences pour le domaine
Définit l'interface attendue par le domaine, à implémenter côté infrastructure
"""
from typing import List, Protocol, Any, Optional


class CompetenceRepository(Protocol):
    """Interface pour l'accès aux données des compétences"""

    async def insert_competence(self, competence: dict) -> Optional[str]:
        """
        Insère une nouvelle compétence dans le référentiel.

        Args:
            competence: Dictionnaire représentant la compétence

        Returns:
            ID de la compétence créée ou None si échec
        """
        ...

    async def get_competence_by_nom(self, nom: str) -> Optional[dict]:
        """
        Récupère une compétence par son nom.

        Args:
            nom: Nom de la compétence

        Returns:
            Document compétence ou None
        """
        ...

    async def get_competences_by_categorie(self, categorie: str) -> List[dict]:
        """
        Récupère toutes les compétences d'une catégorie.

        Args:
            categorie: Nom de la catégorie

        Returns:
            Liste des compétences de la catégorie
        """
        ...

    async def search_competences(self, terme: str, limit: int = 20) -> List[dict]:
        """
        Recherche de compétences par terme.

        Args:
            terme: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste des compétences correspondantes
        """
        ...

    async def update_popularite_competence(
        self, nom: str, nouvelle_popularite: float
    ) -> bool:
        """
        Met à jour la popularité d'une compétence.

        Args:
            nom: Nom de la compétence
            nouvelle_popularite: Nouvelle valeur de popularité (0.0-1.0)

        Returns:
            True si mise à jour réussie
        """
        ...

    async def log_detection_competence(
        self, offre_id: str, competences_detectees: List[dict]
    ) -> bool:
        """
        Enregistre les compétences détectées dans une offre.

        Args:
            offre_id: ID de l'offre
            competences_detectees: Liste des compétences détectées

        Returns:
            True si enregistrement réussi
        """
        ...

    async def get_competences_populaires(self, limit: int = 50) -> List[dict]:
        """
        Récupère les compétences les plus populaires.

        Args:
            limit: Nombre de compétences à retourner

        Returns:
            Liste des compétences triées par popularité
        """
        ...

    async def get_competences_emergentes(
        self, seuil_croissance: float = 0.2, limit: int = 20
    ) -> List[dict]:
        """
        Identifie les compétences émergentes.

        Args:
            seuil_croissance: Seuil de croissance pour considérer comme émergente
            limit: Nombre maximum de résultats

        Returns:
            Liste des compétences émergentes
        """
        ...

    async def sync_competences_from_detections(self) -> dict:
        """
        Synchronise les compétences depuis les détections.

        Returns:
            Statistiques de synchronisation
        """
        ...
