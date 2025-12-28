"""
Service de collecte automatisée des offres d'emploi
Orchestre la collecte depuis France Travail et Adzuna
"""

from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend_v2.shared import logger
from backend_v2.config import Config
from backend_v2.infrastructure.database.mongodb import MongoDBConnection


class CollectionService:
    """Service de collecte d'offres depuis toutes les sources"""

    def __init__(self):
        self.db_connection = MongoDBConnection()
        self.logger = logger.bind(service="CollectionService")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Accès à la base de données"""
        return self.db_connection.async_db

    async def collect_all_sources(
        self,
        max_offres_per_source: int | None = None
    ) -> Dict[str, Any]:
        """
        Collecte des offres depuis toutes les sources disponibles

        Args:
            max_offres_per_source: Nombre max d'offres par source

        Returns:
            Statistiques de la collecte
        """
        self.logger.info("Début de la collecte multi-sources")

        results = {
            "success": True,
            "timestamp": datetime.now(),
            "sources": {},
            "total_nouvelles_offres": 0,
            "total_doublons": 0,
        }

        # 1. Collecter France Travail
        try:
            ft_result = await self._collect_france_travail(max_offres_per_source)
            results["sources"]["francetravail"] = ft_result
            results["total_nouvelles_offres"] += ft_result["nouvelles_offres"]
            results["total_doublons"] += ft_result["doublons"]
        except Exception as e:
            self.logger.error(f"Erreur collecte France Travail: {e}")
            results["sources"]["francetravail"] = {"error": str(e)}

        # 2. Collecter Adzuna
        try:
            adzuna_result = await self._collect_adzuna(max_offres_per_source)
            results["sources"]["adzuna"] = adzuna_result
            results["total_nouvelles_offres"] += adzuna_result["nouvelles_offres"]
            results["total_doublons"] += adzuna_result["doublons"]
        except Exception as e:
            self.logger.error(f"Erreur collecte Adzuna: {e}")
            results["sources"]["adzuna"] = {"error": str(e)}

        # 3. Extraction des compétences pour les nouvelles offres
        if results["total_nouvelles_offres"] > 0:
            try:
                extraction_result = await self._extract_competences_nouvelles_offres()
                results["extraction_competences"] = extraction_result
            except Exception as e:
                self.logger.error(f"Erreur extraction compétences: {e}")
                results["extraction_competences"] = {"error": str(e)}

        # 4. Enregistrer l'exécution
        await self._save_execution_log(results)

        self.logger.info(
            "Collecte multi-sources terminée",
            nouvelles_offres=results["total_nouvelles_offres"],
            doublons=results["total_doublons"]
        )

        return results

    async def _collect_france_travail(self, max_offres: int) -> Dict[str, Any]:
        """Collecte depuis France Travail API"""
        from backend_v2.infrastructure.clients.france_travail_api import FranceTravailAPIClient
        from backend_v2.domain.entities.job import Job

        self.logger.info("Collecte France Travail démarrée", max_offres=max_offres)

        client = FranceTravailAPIClient()

        # Codes ROME pour les métiers du développement IT
        codes_rome = ["M1805", "M1802", "M1810"]

        toutes_offres_brutes = []
        for code_rome in codes_rome:
            self.logger.info(f"Collecte France Travail pour code ROME {code_rome}")
            offres_rome = client.collect_offres_by_rome(
                code_rome=code_rome,
                max_offres=max_offres // len(codes_rome) if max_offres else 500
            )
            toutes_offres_brutes.extend(offres_rome)

        offres_brutes = toutes_offres_brutes

        self.logger.info(f"France Travail: {len(offres_brutes)} offres brutes récupérées")

        nouvelles = 0
        doublons = 0

        for offre_brute in offres_brutes:
            try:
                # Convertir en entité Job
                job = Job.from_api(offre_brute)

                # Vérifier si existe déjà
                existing = await self.db.offres.find_one({
                    "source": "francetravail",
                    "source_id": job.source_id
                })

                if not existing:
                    # Insérer dans MongoDB
                    job_dict = job.to_dict()
                    job_dict["source"] = "francetravail"
                    await self.db.offres.insert_one(job_dict)
                    nouvelles += 1
                else:
                    doublons += 1

            except Exception as e:
                self.logger.error(f"Erreur traitement offre France Travail: {e}")

        return {
            "nouvelles_offres": nouvelles,
            "doublons": doublons,
            "total_collectees": len(offres_brutes),
        }

    async def _collect_adzuna(self, max_offres: int) -> Dict[str, Any]:
        """Collecte depuis Adzuna API"""
        from backend_v2.infrastructure.clients.adzuna_api import AdzunaAPIClient

        self.logger.info("Collecte Adzuna démarrée", max_offres=max_offres)

        # Vérifier credentials
        if not Config.ADZUNA_APP_ID or not Config.ADZUNA_CLIENT_SECRET:
            self.logger.warning("Credentials Adzuna manquants, collecte ignorée")
            return {
                "nouvelles_offres": 0,
                "doublons": 0,
                "total_collectees": 0,
                "skipped": True,
            }

        client = AdzunaAPIClient()

        params = {
            "category": "it-jobs",
            "what": "developpeur",
            "max_days_old": 7,  # Offres des 7 derniers jours seulement
        }

        offres_brutes = client.collect_offres_paginated(
            params=params,
            page_size=50,
            max_offres=max_offres if max_offres else 1500
        )

        nouvelles = 0
        doublons = 0

        for offre_brute in offres_brutes:
            try:
                # Convertir au format MongoDB
                offre_db = self._convert_adzuna_to_db(offre_brute)

                # Vérifier si existe déjà
                existing = await self.db.offres.find_one({
                    "source": "adzuna",
                    "source_id": offre_db["source_id"]
                })

                if not existing:
                    await self.db.offres.insert_one(offre_db)
                    nouvelles += 1
                else:
                    doublons += 1

            except Exception as e:
                self.logger.error(f"Erreur traitement offre Adzuna: {e}")

        return {
            "nouvelles_offres": nouvelles,
            "doublons": doublons,
            "total_collectees": len(offres_brutes),
        }

    def _convert_adzuna_to_db(self, adzuna_offre: dict) -> dict:
        """Convertir une offre Adzuna au format MongoDB"""
        location = adzuna_offre.get("location", {})
        location_display = location.get("display_name", "")

        return {
            "source": "adzuna",
            "source_id": str(adzuna_offre.get("id", "")),
            "intitule": adzuna_offre.get("title", ""),
            "description": adzuna_offre.get("description", ""),
            "date_creation": datetime.fromisoformat(
                adzuna_offre.get("created").replace("Z", "+00:00")
            ) if adzuna_offre.get("created") else datetime.now(),
            "date_actualisation": None,
            "date_insertion": datetime.now(),
            "url_offre": adzuna_offre.get("redirect_url", ""),
            "type_contrat": adzuna_offre.get("contract_type", "Non spécifié"),
            "type_contrat_libelle": adzuna_offre.get("contract_type", "Non spécifié"),
            "lieu_travail": {
                "libelle": location_display,
                "latitude": area[1] if (area := location.get("area")) and len(area) > 1 else None,
                "longitude": area[0] if (area := location.get("area")) and len(area) > 0 else None,
                "codePostal": None,
                "commune": location_display.split(",")[0] if "," in location_display else location_display,
            },
            "entreprise": {
                "nom": adzuna_offre.get("company", {}).get("display_name", ""),
                "entrepriseAdaptee": False,
            },
            "salaire": {
                "libelle": f"{adzuna_offre.get('salary_min', '')} - {adzuna_offre.get('salary_max', '')}" if adzuna_offre.get('salary_min') else None,
            },
            "competences": [],
            "competences_extraites": [],
            "is_active": True,
            "traite": False,
            "origine": 2,
            "raw_data": adzuna_offre,
        }

    async def _extract_competences_nouvelles_offres(self) -> Dict[str, Any]:
        """Extraire les compétences des offres non traitées via CompetenceAnalyzer"""
        from backend_v2.domain.services import SemanticCompetenceAnalyzer as CompetenceAnalyzer

        self.logger.info("Extraction des compétences pour nouvelles offres")

        # Récupérer les offres non traitées
        query = {
            "$or": [
                {"competences_extraites": {"$exists": False}},
                {"competences_extraites": []},
                {"traite": False},
            ]
        }

        cursor = self.db.offres.find(query)
        offres_a_analyser = await cursor.to_list(length=None)

        if not offres_a_analyser:
            self.logger.info("Aucune offre à analyser")
            return {"offres_analysees": 0, "offres_avec_competences": 0}

        # Créer l'analyzer (utilise competences.json de backend_v2/data par défaut)
        analyzer = CompetenceAnalyzer()

        # Analyser chaque offre
        nb_mises_a_jour = 0
        nb_avec_competences = 0
        total_offres = len(offres_a_analyser)
        self.logger.info(f"Début extraction compétences pour {total_offres} offres")

        for i, offre in enumerate(offres_a_analyser):
            if (i + 1) % 100 == 0:
                self.logger.info(f"Extraction compétences: {i + 1}/{total_offres} offres traitées")
            # Construire le texte à analyser
            texte = f"{offre.get('intitule', '')}\n\n{offre.get('description', '')}"

            # Extraire les compétences
            matches = analyzer.analyze_text(texte)

            # Récupérer les noms de compétences et les scores
            competences = [m.nom for m in matches]
            competences_scores = {m.nom: m.score for m in matches}

            if competences:
                nb_avec_competences += 1

            # Mettre à jour MongoDB
            result = await self.db.offres.update_one(
                {"_id": offre["_id"]},
                {
                    "$set": {
                        "competences_extraites": competences,
                        "competences_scores": competences_scores,
                        "traite": True,
                        "date_traitement": datetime.now(),
                    }
                }
            )

            if result.modified_count > 0:
                nb_mises_a_jour += 1

        self.logger.info(
            "Extraction terminée",
            offres_analysees=len(offres_a_analyser),
            offres_mises_a_jour=nb_mises_a_jour
        )

        return {
            "offres_analysees": len(offres_a_analyser),
            "offres_avec_competences": nb_avec_competences,
            "offres_mises_a_jour": nb_mises_a_jour,
        }

    async def _save_execution_log(self, results: Dict[str, Any]):
        """Sauvegarder le log d'exécution de la collecte"""
        try:
            await self.db.collection_executions.insert_one({
                "timestamp": results["timestamp"],
                "total_nouvelles_offres": results["total_nouvelles_offres"],
                "total_doublons": results["total_doublons"],
                "sources": results["sources"],
                "extraction_competences": results.get("extraction_competences"),
            })
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde log: {e}")
