"""
Repository Stats - Accès aux statistiques et métriques
Gestion des données agrégées et calculs de tendances
"""

from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from ...models.competence import CompetenceStats


class StatsRepository:
    """Repository pour les statistiques et analyses"""

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialise le repository

        Args:
            database: Instance de base MongoDB
        """
        self.db = database
        self.collection_stats = database.stats_competences
        self.collection_offres = database.offres
        # Alias pour compatibilité (collection par défaut = stats)
        self.collection = self.collection_stats

    async def save_competence_stats(self, stats: CompetenceStats) -> bool:
        """
        Sauvegarde les statistiques de compétences

        Args:
            stats: Modèle de statistiques à sauvegarder

        Returns:
            True si sauvegarde réussie
        """
        try:
            stats_dict = stats.dict()

            # Upsert basé sur la période
            await self.collection_stats.replace_one(
                {"periode_analysee": stats.periode_analysee}, stats_dict, upsert=True
            )
            return True

        except Exception as e:
            print(f"❌ Erreur sauvegarde stats: {e}")
            return False

    async def get_latest_stats(self) -> dict[str, Any] | None:
        """
        Récupère les dernières statistiques disponibles

        Returns:
            Document des dernières statistiques
        """
        cursor = (
            self.collection_stats.find({}).sort("date_analyse", DESCENDING).limit(1)
        )
        results = await cursor.to_list(length=1)
        return results[0] if results else None

    async def get_stats_by_periode(self, periode: str) -> dict[str, Any] | None:
        """
        Récupère les statistiques d'une période spécifique

        Args:
            periode: Période au format "YYYY-MM" ou "YYYY-QN"

        Returns:
            Statistiques de la période ou None
        """
        return await self.collection_stats.find_one({"periode_analysee": periode})

    async def get_evolution_competence(
        self, competence: str, nb_periodes: int = 12
    ) -> list[dict[str, Any]]:
        """
        Récupère l'évolution d'une compétence sur plusieurs périodes

        Args:
            competence: Nom de la compétence
            nb_periodes: Nombre de périodes à récupérer

        Returns:
            Liste des points d'évolution
        """
        cursor = (
            self.collection_stats.find({"competences_stats.competence": competence})
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

        return evolution

    async def calculate_realtime_stats(self, jours: int = 30) -> dict[str, Any]:
        """
        Calcule des statistiques temps réel sur les N derniers jours

        Args:
            jours: Nombre de jours à analyser

        Returns:
            Statistiques temps réel
        """
        date_limite = datetime.now() - timedelta(days=jours)

        # Pipeline d'agrégation pour stats temps réel
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

        # Stats globales
        total_offres = await self.collection_offres.count_documents(
            {"date_creation": {"$gte": date_limite}}
        )

        # Transformation en format standard
        stats_competences = []
        for comp_stat in competences_stats:
            pourcentage = (
                (comp_stat["nb_offres"] / total_offres) * 100 if total_offres > 0 else 0
            )
            stats_competences.append(
                {
                    "competence": comp_stat["_id"],
                    "nb_offres": comp_stat["nb_offres"],
                    "pourcentage": round(pourcentage, 2),
                }
            )

        return {
            "periode_analysee": f"realtime_{jours}j",
            "date_analyse": datetime.now(),
            "nb_offres_analysees": total_offres,
            "competences_stats": stats_competences,
            "top_competences": [c["competence"] for c in stats_competences[:10]],
        }

    async def get_tendances_competences(
        self, seuil_croissance: float = 0.1
    ) -> dict[str, list[str]]:
        """
        Identifie les tendances d'évolution des compétences

        Args:
            seuil_croissance: Seuil pour détecter croissance/déclin (10% par défaut)

        Returns:
            Dict avec listes de compétences croissantes/déclinantes/stables
        """
        # Récupérer les 2 dernières périodes pour comparaison
        cursor = (
            self.collection_stats.find({}).sort("date_analyse", DESCENDING).limit(2)
        )
        periodes = await cursor.to_list(length=2)

        if len(periodes) < 2:
            return {"croissantes": [], "declinantes": [], "stables": []}

        periode_actuelle = periodes[0]
        periode_precedente = periodes[1]

        # Créer des maps pour comparaison
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
                # Nouvelle compétence apparue
                if pourcentage_actuel >= 1.0:  # Seuil minimum d'apparition
                    croissantes.append(competence)

        return {
            "croissantes": croissantes[:20],
            "declinantes": declinantes[:20],
            "stables": stables[:20],
        }

    async def get_stats_geographiques(
        self, competence: str | None = None
    ) -> dict[str, Any]:
        """
        Calcule les statistiques géographiques

        Args:
            competence: Compétence spécifique (optionnel)

        Returns:
            Statistiques par région/département
        """
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

        # Transformation pour faciliter l'usage
        par_departement = {}
        par_region = {}

        for stat in stats_geo:
            dept = stat["_id"]["departement"]
            region = stat["_id"]["region"]
            nb_offres = stat["nb_offres"]

            if dept:
                par_departement[dept] = nb_offres
            if region:
                par_region[region] = par_region.get(region, 0) + nb_offres

        return {
            "par_departement": par_departement,
            "par_region": par_region,
            "total_zones": len(stats_geo),
        }

    async def cleanup_old_stats(self, nb_periodes_a_garder: int = 24) -> int:
        """
        Nettoie les anciennes statistiques

        Args:
            nb_periodes_a_garder: Nombre de périodes à conserver

        Returns:
            Nombre de documents supprimés
        """
        # Récupérer les périodes à garder
        cursor = (
            self.collection_stats.find({})
            .sort("date_analyse", DESCENDING)
            .limit(nb_periodes_a_garder)
        )
        periodes_a_garder = await cursor.to_list(length=nb_periodes_a_garder)

        if len(periodes_a_garder) < nb_periodes_a_garder:
            return 0  # Pas assez de périodes pour nettoyer

        date_limite = periodes_a_garder[-1]["date_analyse"]

        result = await self.collection_stats.delete_many(
            {"date_analyse": {"$lt": date_limite}}
        )

        print(f"🗑️ {result.deleted_count} anciennes statistiques supprimées")
        return result.deleted_count
