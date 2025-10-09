"""
Repository Compétences - Accès aux données des compétences
Gestion des compétences, détection et normalisation
"""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from ...models.competence import CompetenceDetectee, CompetenceModel


class CompetencesRepository:
    """Repository pour les compétences et leur gestion"""

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialise le repository

        Args:
            database: Instance de base MongoDB
        """
        self.db = database
        self.collection = database.competences
        self.collection_detections = database.competences_detections

    async def insert_competence(self, competence: CompetenceModel) -> str | None:
        """
        Insère une nouvelle compétence dans le référentiel

        Args:
            competence: Modèle de compétence

        Returns:
            ID de la compétence créée
        """
        try:
            competence_dict = competence.dict()
            result = await self.collection.insert_one(competence_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Erreur insertion compétence: {e}")
            return None

    async def get_competence_by_nom(self, nom: str) -> dict[str, Any] | None:
        """
        Récupère une compétence par son nom

        Args:
            nom: Nom de la compétence

        Returns:
            Document compétence ou None
        """
        return await self.collection.find_one(
            {
                "$or": [
                    {"nom": {"$regex": f"^{nom}$", "$options": "i"}},
                    {"nom_normalise": nom.lower()},
                    {"synonymes": {"$regex": f"^{nom}$", "$options": "i"}},
                ]
            }
        )

    async def get_competences_by_categorie(
        self, categorie: str
    ) -> list[dict[str, Any]]:
        """
        Récupère toutes les compétences d'une catégorie

        Args:
            categorie: Nom de la catégorie

        Returns:
            Liste des compétences de la catégorie
        """
        cursor = self.collection.find({"categorie": categorie}).sort(
            "popularite", DESCENDING
        )
        return await cursor.to_list(length=None)

    async def search_competences(
        self, terme: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Recherche de compétences par terme

        Args:
            terme: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste des compétences correspondantes
        """
        cursor = (
            self.collection.find(
                {
                    "$or": [
                        {"nom": {"$regex": terme, "$options": "i"}},
                        {"synonymes": {"$regex": terme, "$options": "i"}},
                        {"description": {"$regex": terme, "$options": "i"}},
                    ]
                }
            )
            .sort("popularite", DESCENDING)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def update_popularite_competence(
        self, nom: str, nouvelle_popularite: float
    ) -> bool:
        """
        Met à jour la popularité d'une compétence

        Args:
            nom: Nom de la compétence
            nouvelle_popularite: Nouvelle valeur de popularité (0.0-1.0)

        Returns:
            True si mise à jour réussie
        """
        try:
            result = await self.collection.update_one(
                {"nom_normalise": nom.lower()},
                {"$set": {"popularite": nouvelle_popularite}},
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Erreur mise à jour popularité: {e}")
            return False

    async def log_detection_competence(
        self, offre_id: str, competences_detectees: list[CompetenceDetectee]
    ) -> bool:
        """
        Enregistre les compétences détectées dans une offre

        Args:
            offre_id: ID de l'offre
            competences_detectees: Liste des compétences détectées

        Returns:
            True si enregistrement réussi
        """
        try:
            detection_doc = {
                "offre_id": offre_id,
                "competences": [comp.dict() for comp in competences_detectees],
                "date_detection": datetime.now(),
                "nb_competences": len(competences_detectees),
            }

            await self.collection_detections.insert_one(detection_doc)
            return True

        except Exception as e:
            print(f"❌ Erreur log détection: {e}")
            return False

    async def get_competences_populaires(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Récupère les compétences les plus populaires

        Args:
            limit: Nombre de compétences à retourner

        Returns:
            Liste des compétences triées par popularité
        """
        cursor = self.collection.find({}).sort("popularite", DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_competences_emergentes(
        self, seuil_croissance: float = 0.2, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Identifie les compétences émergentes

        Args:
            seuil_croissance: Seuil de croissance pour considérer comme émergente
            limit: Nombre maximum de résultats

        Returns:
            Liste des compétences émergentes
        """
        # Pipeline d'agrégation pour calculer la croissance
        pipeline = [
            {"$match": {"popularite": {"$exists": True}}},
            {
                "$addFields": {
                    "croissance_estimee": {
                        "$cond": [
                            {"$gt": ["$popularite", 0.1]},
                            {"$multiply": ["$popularite", 2]},
                            "$popularite",
                        ]
                    }
                }
            },
            {"$match": {"croissance_estimee": {"$gte": seuil_croissance}}},
            {"$sort": {"croissance_estimee": DESCENDING}},
            {"$limit": limit},
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def sync_competences_from_detections(self) -> dict[str, int]:
        """
        Synchronise les compétences depuis les détections pour mise à jour automatique

        Returns:
            Statistiques de synchronisation
        """
        # Agrégation pour compter les détections par compétence
        pipeline = [
            {"$unwind": "$competences"},
            {
                "$group": {
                    "_id": "$competences.competence",
                    "nb_detections": {"$sum": 1},
                    "confiance_moyenne": {"$avg": "$competences.confiance"},
                }
            },
            {"$sort": {"nb_detections": DESCENDING}},
        ]

        cursor = self.collection_detections.aggregate(pipeline)
        stats_detections = await cursor.to_list(length=None)

        # Mise à jour des popularités
        updates_count = 0
        for stat in stats_detections:
            competence_nom = stat["_id"]
            nouvelle_popularite = min(
                stat["confiance_moyenne"] * stat["nb_detections"] / 1000, 1.0
            )

            if await self.update_popularite_competence(
                competence_nom, nouvelle_popularite
            ):
                updates_count += 1

        return {
            "competences_analysees": len(stats_detections),
            "competences_mises_a_jour": updates_count,
            "top_competence": stats_detections[0]["_id"] if stats_detections else None,
        }
