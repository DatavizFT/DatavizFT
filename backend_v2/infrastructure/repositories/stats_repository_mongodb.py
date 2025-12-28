"""
Implémentation MongoDB du StatsRepository pour l'infrastructure
"""

from datetime import datetime, timedelta
from typing import List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from backend_v2.domain.repositories.stats_repository import StatsRepository
from backend_v2.shared import logger


class StatsRepositoryMongoDB(StatsRepository):
    """Implémentation MongoDB pour l'accès aux statistiques"""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "stats_competences"):
        self.db = db
        self.collection_stats = db[collection_name]
        self.collection_offres = db["offres"]
        self.collection = self.collection_stats  # Alias pour compatibilité
        self.logger = logger.bind(
            repository="StatsRepositoryMongoDB", collection=collection_name
        )
        self.logger.info(
            "[StatsRepositoryMongoDB] Initialisation du repository MongoDB",
            collection=collection_name,
        )

    async def save_competence_stats(self, stats: dict) -> bool:
        """
        Sauvegarde les statistiques de compétences (upsert basé sur la période).
        """
        periode = stats.get("periode_analysee")
        self.logger.info(
            "[StatsRepositoryMongoDB] Sauvegarde statistiques", periode=periode
        )
        try:
            await self.collection_stats.replace_one(
                {"periode_analysee": periode}, stats, upsert=True
            )
            self.logger.info(
                "[StatsRepositoryMongoDB] Statistiques sauvegardées", periode=periode
            )
            return True
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur sauvegarde stats", error=str(e)
            )
            return False

    async def get_latest_stats(self) -> Optional[dict]:
        """
        Récupère les dernières statistiques disponibles.
        """
        self.logger.info("[StatsRepositoryMongoDB] Récupération dernières statistiques")
        try:
            cursor = (
                self.collection_stats.find({}).sort("date_analyse", DESCENDING).limit(1)
            )
            results = await cursor.to_list(length=1)
            result = results[0] if results else None
            self.logger.info(
                "[StatsRepositoryMongoDB] Dernières stats récupérées",
                found=result is not None,
            )
            return result
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur récupération dernières stats",
                error=str(e),
            )
            raise

    async def get_stats_by_periode(self, periode: str) -> Optional[dict]:
        """
        Récupère les statistiques d'une période spécifique.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Récupération stats par période", periode=periode
        )
        try:
            result = await self.collection_stats.find_one({"periode_analysee": periode})
            self.logger.info(
                "[StatsRepositoryMongoDB] Résultat recherche période",
                periode=periode,
                found=result is not None,
            )
            return result
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur récupération par période",
                error=str(e),
            )
            raise

    async def get_evolution_competence(
        self, competence: str, nb_periodes: int = 12
    ) -> List[dict]:
        """
        Récupère l'évolution d'une compétence sur plusieurs périodes.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Récupération évolution compétence",
            competence=competence,
            nb_periodes=nb_periodes,
        )
        try:
            cursor = (
                self.collection_stats.find(
                    {"competences_stats.competence": competence}
                )
                .sort("date_analyse", DESCENDING)
                .limit(nb_periodes)
            )
            stats_list = await cursor.to_list(length=nb_periodes)

            evolution = []
            for stats_doc in reversed(stats_list):  # Ordre chronologique
                for comp_stat in stats_doc.get("competences_stats", []):
                    if comp_stat["competence"] == competence:
                        evolution.append(
                            {
                                "periode": stats_doc["periode_analysee"],
                                "date": stats_doc["date_analyse"],
                                "nb_offres": comp_stat["nb_offres"],
                                "pourcentage": comp_stat["pourcentage"],
                                "salaire_moyen": comp_stat.get("salaire_moyen"),
                            }
                        )
                        break

            self.logger.info(
                "[StatsRepositoryMongoDB] Évolution récupérée",
                competence=competence,
                nb_points=len(evolution),
            )
            return evolution
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur récupération évolution", error=str(e)
            )
            raise

    async def calculate_realtime_stats(self, jours: int = 30) -> dict:
        """
        Calcule des statistiques temps réel sur les N derniers jours.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Calcul stats temps réel", jours=jours
        )
        try:
            date_limite = datetime.now() - timedelta(days=jours)

            pipeline = [
                {"$match": {"date_creation": {"$gte": date_limite}}},
                {"$unwind": "$competences_extraites"},
                {
                    "$group": {
                        "_id": "$competences_extraites",
                        "nb_offres": {"$sum": 1},
                        "offres_recentes": {"$addToSet": "$source_id"},
                    }
                },
                {"$sort": {"nb_offres": DESCENDING}},
                {"$limit": 50},
            ]

            cursor = self.collection_offres.aggregate(pipeline)
            competences_stats = await cursor.to_list(length=50)

            total_offres = await self.collection_offres.count_documents(
                {"date_creation": {"$gte": date_limite}}
            )

            stats_competences = []
            for comp_stat in competences_stats:
                pourcentage = (
                    (comp_stat["nb_offres"] / total_offres) * 100
                    if total_offres > 0
                    else 0
                )
                stats_competences.append(
                    {
                        "competence": comp_stat["_id"],
                        "nb_offres": comp_stat["nb_offres"],
                        "pourcentage": round(pourcentage, 2),
                    }
                )

            result = {
                "periode_analysee": f"realtime_{jours}j",
                "date_analyse": datetime.now(),
                "nb_offres_analysees": total_offres,
                "competences_stats": stats_competences,
                "top_competences": [c["competence"] for c in stats_competences[:10]],
            }
            self.logger.info(
                "[StatsRepositoryMongoDB] Stats temps réel calculées",
                nb_offres=total_offres,
                nb_competences=len(stats_competences),
            )
            return result
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur calcul stats temps réel", error=str(e)
            )
            raise

    async def get_tendances_competences(
        self, seuil_croissance: float = 0.1
    ) -> dict:
        """
        Identifie les tendances d'évolution des compétences.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Analyse tendances",
            seuil_croissance=seuil_croissance,
        )
        try:
            cursor = (
                self.collection_stats.find({}).sort("date_analyse", DESCENDING).limit(2)
            )
            periodes = await cursor.to_list(length=2)

            if len(periodes) < 2:
                self.logger.info(
                    "[StatsRepositoryMongoDB] Pas assez de périodes pour les tendances"
                )
                return {"croissantes": [], "declinantes": [], "stables": []}

            periode_actuelle = periodes[0]
            periode_precedente = periodes[1]

            stats_actuelles = {
                stat["competence"]: stat["pourcentage"]
                for stat in periode_actuelle.get("competences_stats", [])
            }
            stats_precedentes = {
                stat["competence"]: stat["pourcentage"]
                for stat in periode_precedente.get("competences_stats", [])
            }

            croissantes = []
            declinantes = []
            stables = []

            for competence, pourcentage_actuel in stats_actuelles.items():
                pourcentage_precedent = stats_precedentes.get(competence, 0)

                if pourcentage_precedent > 0:
                    variation = (
                        pourcentage_actuel - pourcentage_precedent
                    ) / pourcentage_precedent

                    if variation >= seuil_croissance:
                        croissantes.append(competence)
                    elif variation <= -seuil_croissance:
                        declinantes.append(competence)
                    else:
                        stables.append(competence)
                else:
                    if pourcentage_actuel >= 1.0:
                        croissantes.append(competence)

            result = {
                "croissantes": croissantes[:20],
                "declinantes": declinantes[:20],
                "stables": stables[:20],
            }
            self.logger.info(
                "[StatsRepositoryMongoDB] Tendances analysées",
                nb_croissantes=len(croissantes),
                nb_declinantes=len(declinantes),
            )
            return result
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur analyse tendances", error=str(e)
            )
            raise

    async def get_stats_geographiques(
        self, competence: Optional[str] = None
    ) -> dict:
        """
        Calcule les statistiques géographiques.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Calcul stats géographiques",
            competence=competence,
        )
        try:
            match_stage = {}
            if competence:
                match_stage["competences_extraites"] = competence.lower()

            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": {
                            "departement": "$localisation.departement",
                            "region": "$localisation.region",
                        },
                        "nb_offres": {"$sum": 1},
                        "competences_top": {"$addToSet": "$competences_extraites"},
                    }
                },
                {"$sort": {"nb_offres": DESCENDING}},
            ]

            cursor = self.collection_offres.aggregate(pipeline)
            stats_geo = await cursor.to_list(length=None)

            par_departement = {}
            par_region = {}

            for stat in stats_geo:
                dept = stat["_id"].get("departement")
                region = stat["_id"].get("region")
                nb_offres = stat["nb_offres"]

                if dept:
                    par_departement[dept] = nb_offres
                if region:
                    par_region[region] = par_region.get(region, 0) + nb_offres

            result = {
                "par_departement": par_departement,
                "par_region": par_region,
                "total_zones": len(stats_geo),
            }
            self.logger.info(
                "[StatsRepositoryMongoDB] Stats géographiques calculées",
                nb_departements=len(par_departement),
                nb_regions=len(par_region),
            )
            return result
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur stats géographiques", error=str(e)
            )
            raise

    async def cleanup_old_stats(self, nb_periodes_a_garder: int = 24) -> int:
        """
        Nettoie les anciennes statistiques.
        """
        self.logger.info(
            "[StatsRepositoryMongoDB] Nettoyage anciennes stats",
            nb_periodes_a_garder=nb_periodes_a_garder,
        )
        try:
            cursor = (
                self.collection_stats.find({})
                .sort("date_analyse", DESCENDING)
                .limit(nb_periodes_a_garder)
            )
            periodes_a_garder = await cursor.to_list(length=nb_periodes_a_garder)

            if len(periodes_a_garder) < nb_periodes_a_garder:
                self.logger.info(
                    "[StatsRepositoryMongoDB] Pas assez de périodes pour nettoyer"
                )
                return 0

            date_limite = periodes_a_garder[-1]["date_analyse"]

            result = await self.collection_stats.delete_many(
                {"date_analyse": {"$lt": date_limite}}
            )

            self.logger.info(
                "[StatsRepositoryMongoDB] Nettoyage terminé",
                nb_supprimees=result.deleted_count,
            )
            return result.deleted_count
        except Exception as e:
            self.logger.error(
                "[StatsRepositoryMongoDB] Erreur nettoyage", error=str(e)
            )
            raise
