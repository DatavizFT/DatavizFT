"""
Competence Processor - Processeur générique d'analyse de compétences
Analyse et extraction des compétences depuis les offres d'emploi
"""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ...data import COMPETENCES_REFERENTIEL
from ...database.repositories import OffresRepository
from ...tools.competence_analyzer import CompetenceAnalyzer
from ...tools.logging_config import get_logger

logger = get_logger(__name__)


class CompetenceProcessor:
    """
    Processeur générique pour l'analyse des compétences
    Analyse les offres et extrait les compétences techniques
    """

    def __init__(
        self,
        source_name: str,
        competences_referentiel: dict[str, list[str]] | None = None,
    ):
        """
        Initialise le processeur de compétences

        Args:
            source_name: Nom de la source des offres
            competences_referentiel: Référentiel de compétences (défaut: COMPETENCES_REFERENTIEL)
        """
        self.source_name = source_name
        self.competences_referentiel = (
            competences_referentiel or COMPETENCES_REFERENTIEL
        )

        # Analyzer de compétences
        self.analyzer = CompetenceAnalyzer(self.competences_referentiel)

        # Repositories (à initialiser via set_database)
        self.offres_repo: OffresRepository | None = None
        self.db: AsyncIOMotorDatabase | None = None

        logger.info(
            f"Processeur de compétences initialisé pour {source_name} - "
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
        logger.debug(f"Base de données configurée pour processeur {self.source_name}")

    async def analyze_jobs_competences(
        self,
        pipeline_name: str,
        limit_jobs: int | None = None,
        analyze_all: bool = True,
        force_reanalyze: bool = False,
    ) -> dict[str, Any]:
        """
        Analyse les compétences des offres d'emploi

        Args:
            pipeline_name: Nom du pipeline (pour tracking)
            limit_jobs: Limite du nombre d'offres à analyser
            analyze_all: Si True, analyse toutes les offres, sinon seulement les récentes
            force_reanalyze: Si True, réanalyse même les offres déjà traitées

        Returns:
            Résultats de l'analyse avec statistiques
        """
        if not self.offres_repo or self.db is None:
            raise RuntimeError(
                f"Base de données non configurée pour {self.source_name}"
            )

        logger.info(f"🧠 Début analyse des compétences pour {self.source_name}")

        try:
            # 1. Récupérer les offres à analyser
            if analyze_all:
                logger.info("🕐 Analyse de TOUTES les offres (séries temporelles)")
                if force_reanalyze:
                    # Toutes les offres de cette source
                    query = {"source": self.source_name}
                else:
                    # Seulement les non traitées de cette source
                    query = {
                        "source": self.source_name,
                        "$or": [
                            {"traite": {"$exists": False}},
                            {"traite": False},
                            {"competences_extraites": {"$exists": False}},
                            {"competences_extraites": []},
                        ],
                    }
            else:
                logger.info("🕐 Analyse des offres récentes (30 derniers jours)")
                from datetime import timedelta

                date_limite = datetime.now() - timedelta(days=30)

                if force_reanalyze:
                    query = {
                        "source": self.source_name,
                        "date_collecte": {"$gte": date_limite},
                    }
                else:
                    query = {
                        "source": self.source_name,
                        "date_collecte": {"$gte": date_limite},
                        "$or": [
                            {"traite": {"$exists": False}},
                            {"traite": False},
                            {"competences_extraites": {"$exists": False}},
                            {"competences_extraites": []},
                        ],
                    }

            # Récupération des offres
            cursor = self.offres_repo.collection.find(query)
            if limit_jobs:
                cursor = cursor.limit(limit_jobs)

            offres_a_analyser = await cursor.to_list(length=limit_jobs)

            if not offres_a_analyser:
                logger.info(f"Aucune offre à analyser pour {self.source_name}")
                return {
                    "success": True,
                    "source": self.source_name,
                    "nb_offres_analysees": 0,
                    "nb_competences_detectees": 0,
                    "nb_offres_mises_a_jour": 0,
                }

            logger.info(
                f"📊 Analyse de {len(offres_a_analyser)} offres pour {self.source_name}"
            )

            # 2. Conversion au format analyzer
            offres_pour_analyse = []
            for offre in offres_a_analyser:
                offres_pour_analyse.append(
                    {
                        "id": offre.get("source_id"),
                        "intitule": offre.get("intitule", ""),
                        "description": offre.get("description", ""),
                    }
                )

            # 3. Analyse avec CompetenceAnalyzer
            resultats_analyse = self.analyzer.analyser_offres(
                offres_pour_analyse, verbose=True
            )

            # 4. Construction du mapping competences_par_offre
            competences_par_offre = self._construire_mapping_competences_offres(
                resultats_analyse, offres_pour_analyse
            )

            # 5. Sauvegarde des détections
            nb_detections = await self._sauvegarder_competences_detectees(
                competences_par_offre, pipeline_name
            )

            # 6. Mise à jour des offres
            nb_offres_mises_a_jour = await self._mettre_a_jour_offres_avec_competences(
                competences_par_offre
            )

            # 7. Enregistrement de l'exécution
            await self._enregistrer_execution_analyse(
                pipeline_name, len(offres_a_analyser), len(competences_par_offre)
            )

            logger.info(
                f"[OK] Analyse terminée pour {self.source_name}: "
                f"{nb_offres_mises_a_jour} offres mises à jour, "
                f"{nb_detections} détections sauvegardées"
            )

            return {
                "success": True,
                "source": self.source_name,
                "nb_offres_analysees": len(offres_a_analyser),
                "nb_competences_detectees": len(competences_par_offre),
                "nb_detections_sauvegardees": nb_detections,
                "nb_offres_mises_a_jour": nb_offres_mises_a_jour,
                "resultats_par_categorie": resultats_analyse.get(
                    "resultats_par_categorie", {}
                ),
            }

        except Exception as e:
            logger.error(f"[ERREUR] Erreur analyse compétences {self.source_name}: {e}")
            return {
                "success": False,
                "source": self.source_name,
                "error": str(e),
                "nb_offres_analysees": 0,
                "nb_competences_detectees": 0,
            }

    def _construire_mapping_competences_offres(
        self, resultats: dict[str, Any], _offres_pour_analyse: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """
        Construit le mapping offre_id -> compétences depuis les résultats analyzer

        Args:
            resultats: Résultats de CompetenceAnalyzer
            offres_pour_analyse: Liste des offres analysées

        Returns:
            Dictionnaire mapping offre_id -> liste des compétences détectées
        """
        competences_par_offre = {}

        # Parcourir les résultats par catégorie
        for _categorie, data_categorie in resultats.get(
            "resultats_par_categorie", {}
        ).items():
            competences_detectees = data_categorie.get("competences", [])

            # Pour chaque compétence détectée dans cette catégorie
            for comp_info in competences_detectees:
                nom_competence = comp_info.get("competence", "")
                offres_avec_competence = comp_info.get("offres", [])

                # Ajouter cette compétence à chaque offre qui la contient
                for offre_info in offres_avec_competence:
                    offre_id = offre_info.get("id", "")
                    if offre_id:
                        if offre_id not in competences_par_offre:
                            competences_par_offre[offre_id] = []

                        # Éviter les doublons
                        if nom_competence not in competences_par_offre[offre_id]:
                            competences_par_offre[offre_id].append(nom_competence)

        logger.info(
            f"Mapping construit: {len(competences_par_offre)} offres avec compétences"
        )
        return competences_par_offre

    async def _sauvegarder_competences_detectees(
        self, competences_par_offre: dict[str, list[str]], pipeline_name: str
    ) -> int:
        """
        Sauvegarde les compétences détectées dans la collection competences_detections

        Args:
            competences_par_offre: Mapping offre_id -> compétences
            pipeline_name: Nom du pipeline pour tracking

        Returns:
            Nombre de détections sauvegardées
        """
        detections = []

        for offre_id, competences_liste in competences_par_offre.items():
            for competence_nom in competences_liste:
                detection = {
                    "offre_id": offre_id,
                    "source": self.source_name,
                    "pipeline_name": pipeline_name,
                    "competence": competence_nom,
                    "methode_detection": "nlp_pattern_matching",
                    "confiance": 1.0,
                    "contexte": "",
                    "date_detection": datetime.now(),
                }
                detections.append(detection)

        if detections:
            # OPTION 1: Sauvegarder détections détaillées (recommandé pour analytics)
            collection = self.db.competences_detections
            await collection.insert_many(detections)
            logger.info(f"{len(detections)} détections de compétences sauvegardées")

            # OPTION 2: Seulement mettre à jour les offres (plus simple)
            # Décommenter si vous voulez désactiver la collection detections
            # logger.info(f"{len(detections)} détections calculées (non sauvegardées)")

            return len(detections)

        return 0

    async def _mettre_a_jour_offres_avec_competences(
        self, competences_par_offre: dict[str, list[str]]
    ) -> int:
        """
        Met à jour les offres avec les compétences détectées

        Args:
            competences_par_offre: Mapping offre_id -> compétences

        Returns:
            Nombre d'offres mises à jour
        """
        if not competences_par_offre:
            logger.warning("Aucun mapping competences_par_offre à traiter")
            return 0

        nb_mises_a_jour = 0

        for offre_id, competences_liste in competences_par_offre.items():
            # Les compétences sont déjà une liste de noms
            competences_noms = (
                competences_liste if isinstance(competences_liste, list) else []
            )

            # Mettre à jour l'offre dans MongoDB
            result = await self.offres_repo.collection.update_one(
                {"source_id": offre_id},
                {
                    "$set": {
                        "competences_extraites": competences_noms,
                        "traite": True,
                        "date_traitement": datetime.now(),
                    }
                },
            )

            if result.modified_count > 0:
                nb_mises_a_jour += 1

        logger.info(f"[OK] {nb_mises_a_jour} offres mises à jour avec compétences")
        return nb_mises_a_jour

    async def _enregistrer_execution_analyse(
        self,
        pipeline_name: str,
        nb_offres_analysees: int,
        nb_offres_avec_competences: int,
    ):
        """
        Enregistre l'exécution de l'analyse pour le throttling

        Args:
            pipeline_name: Nom du pipeline
            nb_offres_analysees: Nombre d'offres analysées
            nb_offres_avec_competences: Nombre d'offres avec compétences détectées
        """
        try:
            await self.db.pipeline_executions.replace_one(
                {"pipeline_name": pipeline_name, "type": "analyse_competences"},
                {
                    "pipeline_name": pipeline_name,
                    "type": "analyse_competences",
                    "source": self.source_name,
                    "derniere_execution": datetime.now(),
                    "nb_offres_analysees": nb_offres_analysees,
                    "nb_offres_avec_competences": nb_offres_avec_competences,
                },
                upsert=True,
            )
            logger.debug(f"Exécution analyse enregistrée pour {pipeline_name}")
        except Exception as e:
            logger.warning(f"Erreur enregistrement exécution analyse: {e}")

    async def get_analysis_stats(self) -> dict[str, Any]:
        """
        Obtient les statistiques d'analyse pour cette source

        Returns:
            Statistiques de l'analyse
        """
        if not self.offres_repo or self.db is None:
            return {"error": "Base de données non configurée"}

        try:
            # Compter les offres traitées de cette source
            nb_offres_total = await self.offres_repo.collection.count_documents(
                {"source": self.source_name}
            )

            nb_offres_traitees = await self.offres_repo.collection.count_documents(
                {"source": self.source_name, "traite": True}
            )

            nb_offres_avec_competences = (
                await self.offres_repo.collection.count_documents(
                    {
                        "source": self.source_name,
                        "competences_extraites": {"$exists": True, "$ne": []},
                    }
                )
            )

            # Dernière analyse
            derniere_analyse = await self.db.pipeline_executions.find_one(
                {"source": self.source_name, "type": "analyse_competences"},
                sort=[("derniere_execution", -1)],
            )

            return {
                "source": self.source_name,
                "nb_offres_total": nb_offres_total,
                "nb_offres_traitees": nb_offres_traitees,
                "nb_offres_avec_competences": nb_offres_avec_competences,
                "pourcentage_traitees": round(
                    (
                        (nb_offres_traitees / nb_offres_total * 100)
                        if nb_offres_total > 0
                        else 0
                    ),
                    2,
                ),
                "pourcentage_avec_competences": round(
                    (
                        (nb_offres_avec_competences / nb_offres_total * 100)
                        if nb_offres_total > 0
                        else 0
                    ),
                    2,
                ),
                "derniere_analyse": (
                    derniere_analyse.get("derniere_execution")
                    if derniere_analyse
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Erreur stats analyse {self.source_name}: {e}")
            return {"source": self.source_name, "error": str(e)}
