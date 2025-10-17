"""
Stats Generator - Générateur de statistiques générique
Calcule les statistiques par catégorie et tendances temporelles
"""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ...data import COMPETENCES_REFERENTIEL
from ...database.repositories import OffresRepository, StatsRepository
from ...tools.logging_config import get_logger

logger = get_logger(__name__)


class StatsGenerator:
    """
    Générateur générique de statistiques pour pipelines multi-sources
    Calcule les statistiques par catégorie de technologies et tendances temporelles
    """
    
    def __init__(
        self,
        source_name: str,
        competences_referentiel: dict[str, list[str]] | None = None
    ):
        """
        Initialise le générateur de statistiques
        
        Args:
            source_name: Nom de la source des données
            competences_referentiel: Référentiel de compétences (défaut: COMPETENCES_REFERENTIEL)
        """
        self.source_name = source_name
        self.competences_referentiel = competences_referentiel or COMPETENCES_REFERENTIEL
        
        # Repositories (à initialiser via set_database)
        self.offres_repo: OffresRepository | None = None
        self.stats_repo: StatsRepository | None = None
        self.db: AsyncIOMotorDatabase | None = None
        
        logger.info(
            f"Générateur de statistiques initialisé pour {source_name} - "
            f"{len(self.competences_referentiel)} catégories"
        )
    
    def set_database(self, db: AsyncIOMotorDatabase):
        """
        Configure l'accès à la base de données
        
        Args:
            db: Instance de base MongoDB
        """
        self.db = db
        self.offres_repo = OffresRepository(db)
        self.stats_repo = StatsRepository(db)
        logger.debug(f"Base de données configurée pour générateur {self.source_name}")
    
    async def generate_complete_statistics(
        self,
        pipeline_name: str,
        include_temporal: bool = True,
        include_categories: bool = True
    ) -> dict[str, Any]:
        """
        Génère les statistiques complètes pour cette source
        
        Args:
            pipeline_name: Nom du pipeline (pour tracking)
            include_temporal: Inclure les statistiques temporelles
            include_categories: Inclure les statistiques par catégorie
            
        Returns:
            Statistiques complètes avec métadonnées
        """
        if not self.offres_repo or not self.stats_repo or self.db is None:
            raise RuntimeError(f"Base de données non configurée pour {self.source_name}")
        
        logger.info(f"📊 Génération des statistiques pour {self.source_name}")
        
        try:
            # 1. Statistiques générales
            stats_collection = await self._get_collection_stats()
            total_offres = stats_collection.get("nb_offres_total", 0)
            
            if total_offres == 0:
                logger.warning(f"Aucune offre trouvée pour {self.source_name}")
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
                stats_par_categorie = await self._calculate_category_statistics(total_offres)
            
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
                
                # NOUVELLES STATISTIQUES PAR CATÉGORIE
                "statistiques_par_categorie": stats_par_categorie,
                
                # Évolution temporelle
                "evolution_temporelle": evolution_temporelle,
                "repartition_mensuelle": stats_collection.get("repartition_mensuelle", []),
                
                # Métadonnées
                "nb_categories_analysees": len(stats_par_categorie),
                "nb_competences_detectees": len(top_competences),
            }
            
            # 6. Sauvegarde des statistiques
            await self._save_statistics(statistiques, pipeline_name)
            
            # 7. Logging des résultats
            await self._log_statistics_summary(statistiques)
            
            logger.info(f"[OK] Statistiques générées pour {self.source_name}")
            
            return {
                "success": True,
                **statistiques,
            }
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur génération statistiques {self.source_name}: {e}")
            return {
                "success": False,
                "source": self.source_name,
                "error": str(e),
                "nb_offres_analysees": 0,
            }
    
    async def _get_collection_stats(self) -> dict[str, Any]:
        """
        Obtient les statistiques générales de la collection pour cette source
        
        Returns:
            Statistiques de collection
        """
        # Nombre total d'offres pour cette source
        nb_offres_total = await self.offres_repo.collection.count_documents({
            "source": self.source_name
        })
        
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
        
        cursor_monthly = self.offres_repo.collection.aggregate(pipeline_monthly)
        repartition_mensuelle = await cursor_monthly.to_list(length=12)
        
        return {
            "nb_offres_total": nb_offres_total,
            "repartition_mensuelle": repartition_mensuelle,
        }
    
    async def _calculate_top_competences(self, total_offres: int) -> list[dict[str, Any]]:
        """
        Calcule le top des compétences individuelles
        
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
        
        cursor = self.offres_repo.collection.aggregate(pipeline_top_competences)
        top_competences_raw = await cursor.to_list(length=20)
        
        return [
            {
                "competence": item["_id"],
                "nb_occurrences": item["count"],
                "pourcentage": round(item["count"] / total_offres * 100, 2),
            }
            for item in top_competences_raw
            if item["_id"]  # Éviter les compétences vides
        ]
    
    async def _calculate_category_statistics(self, total_offres: int) -> dict[str, Any]:
        """
        Calcule les statistiques par catégorie de technologies
        
        Args:
            total_offres: Nombre total d'offres
            
        Returns:
            Statistiques détaillées par catégorie
        """
        stats_par_categorie = {}
        
        logger.info(f"Calcul des statistiques par catégorie pour {self.source_name}")
        
        for nom_categorie, technologies in self.competences_referentiel.items():
            # Compter les offres contenant au moins une technologie de cette catégorie
            pipeline_categorie = [
                {
                    "$match": {
                        "source": self.source_name,
                        "competences_extraites": {
                            "$in": technologies  # Offres contenant au moins une techno de la catégorie
                        }
                    }
                },
                {"$count": "nb_offres_avec_categorie"}
            ]
            
            cursor_cat = self.offres_repo.collection.aggregate(pipeline_categorie)
            result_cat = await cursor_cat.to_list(1)
            
            nb_offres_avec_categorie = result_cat[0]["nb_offres_avec_categorie"] if result_cat else 0
            pourcentage_categorie = round((nb_offres_avec_categorie / total_offres) * 100, 2)
            
            # Détail des technologies de cette catégorie
            pipeline_detail_categorie = [
                {"$match": {"source": self.source_name}},
                {"$unwind": "$competences_extraites"},
                {
                    "$match": {
                        "competences_extraites": {"$in": technologies}
                    }
                },
                {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            cursor_detail = self.offres_repo.collection.aggregate(pipeline_detail_categorie)
            technologies_detail = await cursor_detail.to_list(None)
            
            stats_par_categorie[nom_categorie] = {
                "nb_offres_avec_categorie": nb_offres_avec_categorie,
                "pourcentage_offres": pourcentage_categorie,
                "nb_technologies_detectees": len(technologies_detail),
                "nb_technologies_disponibles": len(technologies),
                "technologies_populaires": [
                    {
                        "nom": tech["_id"],
                        "nb_occurrences": tech["count"],
                        "pourcentage": round((tech["count"] / total_offres) * 100, 2)
                    }
                    for tech in technologies_detail[:10]  # Top 10 de la catégorie
                ]
            }
        
        return stats_par_categorie
    
    async def _calculate_temporal_evolution(self) -> list[dict[str, Any]]:
        """
        Calcule l'évolution temporelle des offres
        
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
            {"$limit": 30},  # Derniers 30 jours
        ]
        
        cursor_temporal = self.offres_repo.collection.aggregate(pipeline_temporal)
        return await cursor_temporal.to_list(length=30)
    
    async def _save_statistics(self, statistiques: dict[str, Any], pipeline_name: str):
        """
        Sauvegarde les statistiques dans MongoDB
        
        Args:
            statistiques: Statistiques calculées
            pipeline_name: Nom du pipeline
        """
        try:
            # Sauvegarder dans collection stats_competences
            await self.stats_repo.collection_stats.replace_one(
                {
                    "source": self.source_name,
                    "periode_analysee": statistiques["periode_analysee"]
                },
                statistiques,
                upsert=True,
            )
            
            # Enregistrer l'exécution pour le throttling
            await self.db.pipeline_executions.replace_one(
                {
                    "pipeline_name": pipeline_name,
                    "type": "statistiques"
                },
                {
                    "pipeline_name": pipeline_name,
                    "type": "statistiques",
                    "source": self.source_name,
                    "derniere_execution": datetime.now(),
                    "nb_offres_analysees": statistiques["nb_offres_analysees"],
                    "nb_categories": statistiques["nb_categories_analysees"],
                },
                upsert=True,
            )
            
            logger.debug(f"Statistiques sauvegardées pour {self.source_name}")
            
        except Exception as e:
            logger.warning(f"Erreur sauvegarde statistiques {self.source_name}: {e}")
    
    async def _log_statistics_summary(self, statistiques: dict[str, Any]):
        """
        Log un résumé des statistiques générées
        
        Args:
            statistiques: Statistiques calculées
        """
        total_offres = statistiques["nb_offres_analysees"]
        nb_competences = statistiques["nb_competences_detectees"]
        nb_categories = statistiques["nb_categories_analysees"]
        
        logger.info(f"📊 Statistiques {self.source_name} générées pour {total_offres} offres:")
        logger.info(f"   - {nb_competences} compétences individuelles détectées")
        logger.info(f"   - {nb_categories} catégories analysées")
        
        # Log des top catégories
        stats_par_categorie = statistiques.get("statistiques_par_categorie", {})
        if stats_par_categorie:
            categories_triees = sorted(
                stats_par_categorie.items(),
                key=lambda x: x[1]["pourcentage_offres"],
                reverse=True
            )
            
            logger.info(f"🏆 Top 5 catégories les plus demandées ({self.source_name}):")
            for nom_cat, stats_cat in categories_triees[:5]:
                logger.info(
                    f"   - {nom_cat}: {stats_cat['pourcentage_offres']}% "
                    f"({stats_cat['nb_offres_avec_categorie']} offres)"
                )
    
    async def get_latest_statistics(self) -> dict[str, Any] | None:
        """
        Récupère les dernières statistiques générées pour cette source
        
        Returns:
            Dernières statistiques ou None si aucune
        """
        if not self.stats_repo:
            return None
        
        try:
            latest_stats = await self.stats_repo.collection_stats.find_one(
                {"source": self.source_name},
                sort=[("date_analyse", -1)]
            )
            
            return latest_stats
            
        except Exception as e:
            logger.error(f"Erreur récupération stats {self.source_name}: {e}")
            return None