"""
StatsGenerator - Générateur de statistiques pour le domaine
==========================================================

Service domaine pour calculer les statistiques de compétences
et tendances temporelles. Utilise les repositories injectés.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

from backend_v2.shared import logger


class JobRepositoryProtocol(Protocol):
    """Protocol pour le repository d'offres (injection de dépendances)"""

    async def count_documents(self, filter_query: dict) -> int:
        ...

    async def aggregate(self, pipeline: List[dict]) -> List[dict]:
        ...


class StatsRepositoryProtocol(Protocol):
    """Protocol pour le repository de stats (injection de dépendances)"""

    async def save_competence_stats(self, stats: dict) -> bool:
        ...

    async def get_latest_stats(self) -> Optional[dict]:
        ...


class StatsGenerator:
    """
    Générateur de statistiques pour les offres d'emploi.

    Calcule les statistiques par catégorie de technologies et tendances temporelles.
    Architecture hexagonale : dépend d'abstractions (repositories), pas d'implémentations.
    """

    def __init__(
        self,
        source_name: str,
        job_repository: JobRepositoryProtocol,
        stats_repository: StatsRepositoryProtocol,
        competences_referentiel: Dict[str, List[str]],
    ):
        """
        Initialise le générateur de statistiques.

        Args:
            source_name: Nom de la source des données
            job_repository: Repository pour accéder aux offres
            stats_repository: Repository pour sauvegarder les stats
            competences_referentiel: Référentiel de compétences {categorie: [competences]}
        """
        self.source_name = source_name
        self.job_repo = job_repository
        self.stats_repo = stats_repository
        self.competences_referentiel = competences_referentiel

        self.logger = logger.bind(
            service="StatsGenerator",
            source=source_name,
            nb_categories=len(competences_referentiel),
        )
        self.logger.info(
            "[StatsGenerator] Initialisé",
            nb_categories=len(competences_referentiel),
        )

    async def generate_complete_statistics(
        self,
        pipeline_name: str,
        include_temporal: bool = True,
        include_categories: bool = True,
    ) -> Dict[str, Any]:
        """
        Génère les statistiques complètes pour cette source.

        Args:
            pipeline_name: Nom du pipeline (pour tracking)
            include_temporal: Inclure les statistiques temporelles
            include_categories: Inclure les statistiques par catégorie

        Returns:
            Statistiques complètes avec métadonnées
        """
        self.logger.info("[StatsGenerator] Génération des statistiques")

        try:
            # 1. Statistiques générales
            stats_collection = await self._get_collection_stats()
            total_offres = stats_collection.get("nb_offres_total", 0)

            if total_offres == 0:
                self.logger.warning("[StatsGenerator] Aucune offre trouvée")
                return {
                    "success": True,
                    "source": self.source_name,
                    "periode_analysee": datetime.now().strftime("%Y-%m"),
                    "date_analyse": datetime.now(),
                    "nb_offres_analysees": 0,
                    "message": "Aucune offre à analyser",
                }

            # 2. Top compétences globales
            top_competences = await self._calculate_top_competences(total_offres)

            # 3. Statistiques par catégorie
            stats_par_categorie = {}
            if include_categories:
                stats_par_categorie = await self._calculate_category_statistics(
                    total_offres
                )

            # 4. Évolution temporelle
            evolution_temporelle = []
            if include_temporal:
                evolution_temporelle = await self._calculate_temporal_evolution()

            # 5. Compilation des statistiques
            statistiques = {
                "source": self.source_name,
                "pipeline_name": pipeline_name,
                "periode_analysee": datetime.now().strftime("%Y-%m"),
                "date_analyse": datetime.now(),
                "nb_offres_analysees": total_offres,
                # Statistiques globales
                "top_competences": top_competences,
                # Statistiques par catégorie
                "statistiques_par_categorie": stats_par_categorie,
                # Évolution temporelle
                "evolution_temporelle": evolution_temporelle,
                "repartition_mensuelle": stats_collection.get(
                    "repartition_mensuelle", []
                ),
                # Métadonnées
                "nb_categories_analysees": len(stats_par_categorie),
                "nb_competences_detectees": len(top_competences),
            }

            # 6. Sauvegarde des statistiques
            await self._save_statistics(statistiques)

            # 7. Logging du résumé
            self._log_statistics_summary(statistiques)

            self.logger.info("[StatsGenerator] Statistiques générées avec succès")

            return {
                "success": True,
                **statistiques,
            }

        except Exception as e:
            self.logger.error(
                "[StatsGenerator] Erreur génération statistiques",
                error=str(e),
            )
            return {
                "success": False,
                "source": self.source_name,
                "error": str(e),
                "nb_offres_analysees": 0,
            }

    async def _get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtient les statistiques générales de la collection pour cette source.

        Returns:
            Statistiques de collection
        """
        # Nombre total d'offres pour cette source
        nb_offres_total = await self.job_repo.count_documents(
            {"source": self.source_name}
        )

        # Répartition mensuelle (derniers 12 mois)
        pipeline_monthly = [
            {"$match": {"source": self.source_name}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_collecte"},
                        "month": {"$month": "$date_collecte"},
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 12},
        ]

        repartition_mensuelle = await self.job_repo.aggregate(pipeline_monthly)

        return {
            "nb_offres_total": nb_offres_total,
            "repartition_mensuelle": repartition_mensuelle,
        }

    async def _calculate_top_competences(
        self, total_offres: int
    ) -> List[Dict[str, Any]]:
        """
        Calcule le top des compétences individuelles.

        Args:
            total_offres: Nombre total d'offres

        Returns:
            Liste des top compétences avec pourcentages
        """
        pipeline_top_competences = [
            {"$match": {"source": self.source_name}},
            {"$unwind": "$competences_extraites"},
            {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20},
        ]

        top_competences_raw = await self.job_repo.aggregate(pipeline_top_competences)

        return [
            {
                "competence": item["_id"],
                "nb_occurrences": item["count"],
                "pourcentage": round(item["count"] / total_offres * 100, 2),
            }
            for item in top_competences_raw
            if item["_id"]  # Éviter les compétences vides
        ]

    async def _calculate_category_statistics(
        self, total_offres: int
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques par catégorie de technologies.

        Args:
            total_offres: Nombre total d'offres

        Returns:
            Statistiques détaillées par catégorie
        """
        stats_par_categorie = {}

        self.logger.debug("[StatsGenerator] Calcul des statistiques par catégorie")

        for nom_categorie, technologies in self.competences_referentiel.items():
            # Compter les offres contenant au moins une technologie de cette catégorie
            pipeline_categorie = [
                {
                    "$match": {
                        "source": self.source_name,
                        "competences_extraites": {"$in": technologies},
                    }
                },
                {"$count": "nb_offres_avec_categorie"},
            ]

            result_cat = await self.job_repo.aggregate(pipeline_categorie)

            nb_offres_avec_categorie = (
                result_cat[0]["nb_offres_avec_categorie"] if result_cat else 0
            )
            pourcentage_categorie = round(
                (nb_offres_avec_categorie / total_offres) * 100, 2
            )

            # Détail des technologies de cette catégorie
            pipeline_detail_categorie = [
                {"$match": {"source": self.source_name}},
                {"$unwind": "$competences_extraites"},
                {"$match": {"competences_extraites": {"$in": technologies}}},
                {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]

            technologies_detail = await self.job_repo.aggregate(pipeline_detail_categorie)

            stats_par_categorie[nom_categorie] = {
                "nb_offres_avec_categorie": nb_offres_avec_categorie,
                "pourcentage_offres": pourcentage_categorie,
                "nb_technologies_detectees": len(technologies_detail),
                "nb_technologies_disponibles": len(technologies),
                "technologies_populaires": [
                    {
                        "nom": tech["_id"],
                        "nb_occurrences": tech["count"],
                        "pourcentage": round((tech["count"] / total_offres) * 100, 2),
                    }
                    for tech in technologies_detail[:10]  # Top 10 de la catégorie
                ],
            }

        return stats_par_categorie

    async def _calculate_temporal_evolution(self) -> List[Dict[str, Any]]:
        """
        Calcule l'évolution temporelle des offres.

        Returns:
            Statistiques temporelles (derniers 30 jours)
        """
        pipeline_temporal = [
            {"$match": {"source": self.source_name}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_collecte"},
                        "month": {"$month": "$date_collecte"},
                        "day": {"$dayOfMonth": "$date_collecte"},
                    },
                    "nb_offres": {"$sum": 1},
                    "offres_ids": {"$push": "$source_id"},
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": 30},
        ]

        return await self.job_repo.aggregate(pipeline_temporal)

    async def _save_statistics(self, statistiques: Dict[str, Any]):
        """
        Sauvegarde les statistiques via le repository.

        Args:
            statistiques: Statistiques calculées
        """
        try:
            await self.stats_repo.save_competence_stats(statistiques)
            self.logger.debug("[StatsGenerator] Statistiques sauvegardées")
        except Exception as e:
            self.logger.warning(
                "[StatsGenerator] Erreur sauvegarde statistiques",
                error=str(e),
            )

    def _log_statistics_summary(self, statistiques: Dict[str, Any]):
        """
        Log un résumé des statistiques générées.

        Args:
            statistiques: Statistiques calculées
        """
        total_offres = statistiques["nb_offres_analysees"]
        nb_competences = statistiques["nb_competences_detectees"]
        nb_categories = statistiques["nb_categories_analysees"]

        self.logger.info(
            "[StatsGenerator] Résumé statistiques",
            total_offres=total_offres,
            nb_competences=nb_competences,
            nb_categories=nb_categories,
        )

        # Log des top catégories
        stats_par_categorie = statistiques.get("statistiques_par_categorie", {})
        if stats_par_categorie:
            categories_triees = sorted(
                stats_par_categorie.items(),
                key=lambda x: x[1]["pourcentage_offres"],
                reverse=True,
            )

            top_5 = categories_triees[:5]
            self.logger.info(
                "[StatsGenerator] Top 5 catégories",
                top_categories=[
                    {
                        "categorie": nom,
                        "pourcentage": stats["pourcentage_offres"],
                        "nb_offres": stats["nb_offres_avec_categorie"],
                    }
                    for nom, stats in top_5
                ],
            )

    async def get_latest_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Récupère les dernières statistiques générées pour cette source.

        Returns:
            Dernières statistiques ou None si aucune
        """
        try:
            return await self.stats_repo.get_latest_stats()
        except Exception as e:
            self.logger.error(
                "[StatsGenerator] Erreur récupération dernières stats",
                error=str(e),
            )
            return None
