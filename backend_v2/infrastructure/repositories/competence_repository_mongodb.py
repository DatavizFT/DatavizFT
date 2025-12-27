"""
Implémentation MongoDB du CompetenceRepository pour l'infrastructure
"""

from datetime import datetime
from typing import List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from backend_v2.domain.repositories.competence_repository import CompetenceRepository
from backend_v2.shared import logger


class CompetenceRepositoryMongoDB(CompetenceRepository):
    """Implémentation MongoDB pour l'accès aux compétences"""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "competences"):
        self.db = db
        self.collection = db[collection_name]
        self.collection_detections = db["competences_detections"]
        self.logger = logger.bind(
            repository="CompetenceRepositoryMongoDB", collection=collection_name
        )
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Initialisation du repository MongoDB",
            collection=collection_name,
        )

    async def insert_competence(self, competence: dict) -> Optional[str]:
        """
        Insère une nouvelle compétence dans le référentiel.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Insertion d'une compétence",
            competence_nom=competence.get("nom"),
        )
        try:
            result = await self.collection.insert_one(competence)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Compétence insérée",
                inserted_id=str(result.inserted_id),
            )
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur insertion compétence", error=str(e)
            )
            return None

    async def get_competence_by_nom(self, nom: str) -> Optional[dict]:
        """
        Récupère une compétence par son nom (recherche flexible).
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Recherche compétence par nom", nom=nom
        )
        try:
            result = await self.collection.find_one(
                {
                    "$or": [
                        {"nom": {"$regex": f"^{nom}$", "$options": "i"}},
                        {"nom_normalise": nom.lower()},
                        {"synonymes": {"$regex": f"^{nom}$", "$options": "i"}},
                    ]
                }
            )
            found = result is not None
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Résultat recherche", nom=nom, found=found
            )
            return result
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur recherche compétence", error=str(e)
            )
            raise

    async def get_competences_by_categorie(self, categorie: str) -> List[dict]:
        """
        Récupère toutes les compétences d'une catégorie.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Récupération compétences par catégorie",
            categorie=categorie,
        )
        try:
            cursor = self.collection.find({"categorie": categorie}).sort(
                "popularite", DESCENDING
            )
            results = await cursor.to_list(length=None)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Compétences récupérées",
                categorie=categorie,
                nb_competences=len(results),
            )
            return results
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur récupération par catégorie",
                error=str(e),
            )
            raise

    async def search_competences(self, terme: str, limit: int = 20) -> List[dict]:
        """
        Recherche de compétences par terme.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Recherche compétences",
            terme=terme,
            limit=limit,
        )
        try:
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
            results = await cursor.to_list(length=limit)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Résultats recherche",
                terme=terme,
                nb_results=len(results),
            )
            return results
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur recherche", error=str(e)
            )
            raise

    async def update_popularite_competence(
        self, nom: str, nouvelle_popularite: float
    ) -> bool:
        """
        Met à jour la popularité d'une compétence.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Mise à jour popularité",
            nom=nom,
            nouvelle_popularite=nouvelle_popularite,
        )
        try:
            result = await self.collection.update_one(
                {"nom_normalise": nom.lower()},
                {"$set": {"popularite": nouvelle_popularite}},
            )
            success = result.modified_count > 0
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Résultat mise à jour",
                nom=nom,
                success=success,
            )
            return success
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur mise à jour popularité",
                error=str(e),
            )
            return False

    async def log_detection_competence(
        self, offre_id: str, competences_detectees: List[dict]
    ) -> bool:
        """
        Enregistre les compétences détectées dans une offre.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Log détection compétences",
            offre_id=offre_id,
            nb_competences=len(competences_detectees),
        )
        try:
            detection_doc = {
                "offre_id": offre_id,
                "competences": competences_detectees,
                "date_detection": datetime.now(),
                "nb_competences": len(competences_detectees),
            }
            await self.collection_detections.insert_one(detection_doc)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Détection enregistrée", offre_id=offre_id
            )
            return True
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur log détection", error=str(e)
            )
            return False

    async def get_competences_populaires(self, limit: int = 50) -> List[dict]:
        """
        Récupère les compétences les plus populaires.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Récupération compétences populaires",
            limit=limit,
        )
        try:
            cursor = (
                self.collection.find({}).sort("popularite", DESCENDING).limit(limit)
            )
            results = await cursor.to_list(length=limit)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Compétences populaires récupérées",
                nb_results=len(results),
            )
            return results
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur récupération populaires",
                error=str(e),
            )
            raise

    async def get_competences_emergentes(
        self, seuil_croissance: float = 0.2, limit: int = 20
    ) -> List[dict]:
        """
        Identifie les compétences émergentes via pipeline d'agrégation.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Recherche compétences émergentes",
            seuil_croissance=seuil_croissance,
            limit=limit,
        )
        try:
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
            results = await cursor.to_list(length=limit)
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Compétences émergentes trouvées",
                nb_results=len(results),
            )
            return results
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur recherche émergentes",
                error=str(e),
            )
            raise

    async def sync_competences_from_detections(self) -> dict:
        """
        Synchronise les compétences depuis les détections pour mise à jour automatique.
        """
        self.logger.info(
            "[CompetenceRepositoryMongoDB] Synchronisation compétences depuis détections"
        )
        try:
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

            updates_count = 0
            for stat in stats_detections:
                competence_nom = stat["_id"]
                if competence_nom is None:
                    continue
                nouvelle_popularite = min(
                    stat["confiance_moyenne"] * stat["nb_detections"] / 1000, 1.0
                )
                if await self.update_popularite_competence(
                    competence_nom, nouvelle_popularite
                ):
                    updates_count += 1

            result = {
                "competences_analysees": len(stats_detections),
                "competences_mises_a_jour": updates_count,
                "top_competence": (
                    stats_detections[0]["_id"] if stats_detections else None
                ),
            }
            self.logger.info(
                "[CompetenceRepositoryMongoDB] Synchronisation terminée", **result
            )
            return result
        except Exception as e:
            self.logger.error(
                "[CompetenceRepositoryMongoDB] Erreur synchronisation", error=str(e)
            )
            raise
