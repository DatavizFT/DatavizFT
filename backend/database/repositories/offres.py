"""
Repository Offres - Accès aux données des offres d'emploi
Gestion CRUD et requêtes avancées pour les offres MongoDB
"""

from datetime import datetime, timedelta
from typing import Any

import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError

from ...models.offre import OffreEmploiModel

logger = structlog.get_logger(__name__)


class OffresRepository:
    """Repository pour les offres d'emploi MongoDB"""

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialise le repository

        Args:
            database: Instance de base MongoDB
        """
        self.db = database
        self.collection = database.offres

    async def insert_offre(self, offre: OffreEmploiModel) -> str | None:
        """
        Insère une nouvelle offre

        Args:
            offre: Modèle d'offre à insérer

        Returns:
            ID MongoDB de l'offre créée, None si erreur
        """
        try:
            # Conversion en dict avec validation Pydantic
            offre_dict = offre.dict()

            result = await self.collection.insert_one(offre_dict)
            return str(result.inserted_id)

        except DuplicateKeyError:
            print(f"⚠️ Offre déjà existante: {offre.source_id}")
            return None
        except Exception as e:
            print(f"❌ Erreur insertion offre: {e}")
            return None

    async def insert_many_offres(self, offres: list[OffreEmploiModel]) -> int:
        """
        Insère plusieurs offres en lot avec déduplication

        Args:
            offres: Liste d'offres à insérer

        Returns:
            Nombre d'offres réellement insérées
        """
        if not offres:
            return 0

        # ✅ Déduplication optimisée avec une seule requête
        source_ids = [offre.source_id for offre in offres]

        # Récupérer tous les source_id existants en une fois
        existing_cursor = self.collection.find(
            {"source_id": {"$in": source_ids}}, {"source_id": 1, "_id": 0}
        )
        existing_source_ids = {doc["source_id"] async for doc in existing_cursor}

        # Filtrer les nouvelles offres
        offres_nouvelles = [
            offre for offre in offres if offre.source_id not in existing_source_ids
        ]

        doublons = len(offres) - len(offres_nouvelles)
        if doublons > 0:
            logger.info(f"{doublons} doublons détectés et ignorés")

        if not offres_nouvelles:
            logger.info("Aucune nouvelle offre à insérer")
            return 0

        try:
            # Conversion en dicts pour nouvelles offres uniquement
            offres_dicts = [offre.dict() for offre in offres_nouvelles]

            result = await self.collection.insert_many(
                offres_dicts,
                ordered=False,  # Continue même si certaines échouent
            )

            nb_inserees = len(result.inserted_ids)
            logger.info(
                f"{nb_inserees} nouvelles offres insérées, {doublons} doublons ignorés"
            )
            return nb_inserees

        except Exception as e:
            logger.error(f"Erreur insertion batch: {e}")
            return 0

    async def get_offre_by_source_id(self, source_id: str) -> dict[str, Any] | None:
        """
        Récupère une offre par son ID source

        Args:
            source_id: ID de l'offre dans le système source

        Returns:
            Document offre ou None si pas trouvée
        """
        return await self.collection.find_one({"source_id": source_id})

    async def get_offres_recentes(
        self, jours: int = 7, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Récupère les offres récentes

        Args:
            jours: Nombre de jours de recul
            limit: Limite du nombre de résultats

        Returns:
            Liste des offres récentes
        """
        date_limite = datetime.now() - timedelta(days=jours)

        cursor = (
            self.collection.find({"date_creation": {"$gte": date_limite}})
            .sort("date_creation", DESCENDING)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def get_toutes_offres(self, limit: int = 10000) -> list[dict[str, Any]]:
        """
        Récupère toutes les offres (pour séries temporelles long terme)

        Args:
            limit: Limite du nombre de résultats

        Returns:
            Liste de toutes les offres triées par date de création
        """
        logger.info(f"Récupération de toutes les offres (limite: {limit})")

        cursor = (
            self.collection.find({})  # Pas de filtre de date
            .sort("date_creation", DESCENDING)  # Plus récentes en premier
            .limit(limit)
        )

        offres = await cursor.to_list(length=limit)
        logger.info(f"{len(offres)} offres récupérées pour analyse time series")
        return offres

    async def get_offres_par_periode(
        self,
        date_debut: datetime | None = None,
        date_fin: datetime | None = None,
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """
        Récupère les offres sur une période spécifique pour time series

        Args:
            date_debut: Date de début (incluse)
            date_fin: Date de fin (incluse)
            limit: Limite du nombre de résultats

        Returns:
            Liste des offres dans la période triées par date
        """
        query = {}

        if date_debut or date_fin:
            query["date_creation"] = {}
            if date_debut:
                query["date_creation"]["$gte"] = date_debut
            if date_fin:
                query["date_creation"]["$lte"] = date_fin

        logger.info(f"Récupération offres période {date_debut} -> {date_fin}")

        cursor = (
            self.collection.find(query).sort("date_creation", DESCENDING).limit(limit)
        )

        offres = await cursor.to_list(length=limit)
        logger.info(f"{len(offres)} offres trouvées dans la période")
        return offres

    async def get_offres_by_competence(
        self, competence: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Récupère les offres contenant une compétence spécifique

        Args:
            competence: Nom de la compétence recherchée
            limit: Nombre maximum d'offres

        Returns:
            Liste des offres avec cette compétence
        """
        cursor = (
            self.collection.find({"competences_extraites": competence.lower()})
            .sort("date_creation", DESCENDING)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def get_offres_by_localisation(
        self,
        departement: str | None = None,
        region: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Récupère les offres par localisation

        Args:
            departement: Code département (ex: "75")
            region: Code région (ex: "11")
            limit: Nombre maximum d'offres

        Returns:
            Liste des offres dans la zone géographique
        """
        query = {}

        if departement:
            query["localisation.departement"] = departement
        elif region:
            query["localisation.region"] = region

        cursor = (
            self.collection.find(query).sort("date_creation", DESCENDING).limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_offres_by_competences(
        self, competences: list[str]
    ) -> dict[str, int]:
        """
        Compte les offres pour chaque compétence

        Args:
            competences: Liste de compétences à compter

        Returns:
            Dictionnaire {competence: nombre_offres}
        """
        pipeline = [
            {"$match": {"competences_extraites": {"$in": competences}}},
            {"$unwind": "$competences_extraites"},
            {"$match": {"competences_extraites": {"$in": competences}}},
            {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
        ]

        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        return {result["_id"]: result["count"] for result in results}

    async def get_stats_temporelles(
        self,
        competence: str | None = None,
        groupby: str = "month",  # "day", "week", "month"
    ) -> list[dict[str, Any]]:
        """
        Récupère les statistiques temporelles d'évolution

        Args:
            competence: Compétence spécifique (optionnel)
            groupby: Granularité temporelle

        Returns:
            Statistiques temporelles
        """
        # Format de groupe selon la granularité
        group_formats = {
            "day": {
                "year": {"$year": "$date_creation"},
                "month": {"$month": "$date_creation"},
                "day": {"$dayOfMonth": "$date_creation"},
            },
            "week": {
                "year": {"$year": "$date_creation"},
                "week": {"$week": "$date_creation"},
            },
            "month": {
                "year": {"$year": "$date_creation"},
                "month": {"$month": "$date_creation"},
            },
        }

        match_stage = {}
        if competence:
            match_stage["competences_extraites"] = competence.lower()

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": group_formats.get(groupby, group_formats["month"]),
                    "nb_offres": {"$sum": 1},
                    "offres_ids": {"$push": "$source_id"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def delete_anciennes_offres(self, jours: int = 365) -> int:
        """
        Supprime les offres anciennes pour nettoyage

        Args:
            jours: Âge limite en jours

        Returns:
            Nombre d'offres supprimées
        """
        date_limite = datetime.now() - timedelta(days=jours)

        result = await self.collection.delete_many(
            {"date_creation": {"$lt": date_limite}}
        )

        print(f"🗑️ {result.deleted_count} offres anciennes supprimées")
        return result.deleted_count

    async def get_collection_stats(self) -> dict[str, Any]:
        """
        Obtient les statistiques de la collection

        Returns:
            Statistiques diverses de la collection
        """
        total_count = await self.collection.count_documents({})

        # Dernières offres
        recent_pipeline = [{"$sort": {"date_creation": DESCENDING}}, {"$limit": 1}]
        recent_cursor = self.collection.aggregate(recent_pipeline)
        recent_results = await recent_cursor.to_list(length=1)

        # Répartition par mois
        monthly_pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_creation"},
                        "month": {"$month": "$date_creation"},
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": DESCENDING}},
            {"$limit": 12},
        ]
        monthly_cursor = self.collection.aggregate(monthly_pipeline)
        monthly_stats = await monthly_cursor.to_list(length=12)

        return {
            "total_offres": total_count,
            "derniere_offre": recent_results[0] if recent_results else None,
            "repartition_mensuelle": monthly_stats,
            "collection_name": "offres",
        }
