"""
Pipeline MongoDB France Travail M1805 - Version adaptée
Pipeline utilisant MongoDB au lieu des fichiers JSON pour le stockage
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..clients.france_travail import FranceTravailAPIClient
from ..config import Config
from ..data import COMPETENCES_REFERENTIEL
from ..database.repositories import (
    CompetencesRepository,
    OffresRepository,
    StatsRepository,
)
from ..models.mongodb.schemas import OffreEmploiModel
from ..tools.competence_analyzer import CompetenceAnalyzer
from ..tools.logging_config import get_logger

logger = get_logger(__name__)


class PipelineMongoDBM1805:
    """Pipeline MongoDB pour collecte et analyse des offres M1805"""

    def __init__(self):
        """Initialise le pipeline MongoDB"""
        self.config = Config()
        self.code_rome = "M1805"
        self.description = "Études et développement informatique"

        # Référentiel de compétences
        self.competences_referentiel = COMPETENCES_REFERENTIEL

        # Clients et outils
        self.api_client = FranceTravailAPIClient()
        self.analyzer = CompetenceAnalyzer(self.competences_referentiel)

        # Base de données (à initialiser)
        self.db: AsyncIOMotorDatabase | None = None
        self.offres_repo: OffresRepository | None = None
        self.competences_repo: CompetencesRepository | None = None
        self.stats_repo: StatsRepository | None = None

        # État des connexions
        self._connections_closed = False

        logger.info(
            f"Pipeline MongoDB M1805 initialisé - {len(self.competences_referentiel)} catégories de compétences"
        )

    async def init_database_connection(self) -> bool:
        """
        Initialise la connexion directe MongoDB

        Returns:
            True si succès, False sinon
        """
        try:
            # Connexion directe avec Motor
            import motor.motor_asyncio

            self.client_mongo = motor.motor_asyncio.AsyncIOMotorClient(
                self.config.MONGODB_URL
            )
            self.db = self.client_mongo[self.config.MONGODB_DATABASE]

            # Test de connexion
            await self.client_mongo.admin.command("ping")

            # Initialiser les repositories
            self.offres_repo = OffresRepository(self.db)
            self.competences_repo = CompetencesRepository(self.db)
            self.stats_repo = StatsRepository(self.db)

            # Initialiser l'analyseur de compétences
            self.analyseur_competences = CompetenceAnalyzer(
                self.competences_referentiel
            )

            # Initialiser le client API
            self.client_api = FranceTravailAPIClient()

            logger.info("✅ Connexion MongoDB directe établie")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB directe: {e}")
            return False

    async def close_database_connection(self):
        """Ferme la connexion MongoDB"""
        if hasattr(self, "_connections_closed") and self._connections_closed:
            logger.debug("Connexions déjà fermées, ignoré")
            return

        try:
            # Fermeture client API (synchrone)
            if hasattr(self, "client_api") and self.client_api:
                self.client_api.close()  # Pas de await - méthode sync
                self.client_api = None

            # Fermeture client MongoDB (synchrone aussi)
            if hasattr(self, "client_mongo") and self.client_mongo:
                self.client_mongo.close()
                self.client_mongo = None

            # Marquer comme fermé pour éviter les doubles appels
            self._connections_closed = True
            logger.info("🔌 Connexions fermées proprement")

        except Exception as e:
            logger.warning(f"Erreur fermeture connexions: {e}")

    async def verifier_derniere_execution(self) -> dict[str, Any]:
        """
        Vérifie si le pipeline a été exécuté dans les 24 dernières heures
        Utilise MongoDB au lieu des fichiers

        Returns:
            Dict contenant le statut et les informations de la dernière exécution
        """
        try:
            # Chercher les offres les plus récentes dans MongoDB
            offres_recentes = await self.offres_repo.get_offres_recentes(
                jours=1, limit=1
            )

            if not offres_recentes:
                return {
                    "doit_executer": True,
                    "raison": "Aucune offre récente dans MongoDB",
                    "derniere_execution": None,
                    "nb_offres_recentes": 0,
                }

            derniere_offre = offres_recentes[0]
            derniere_execution = derniere_offre.get("date_creation")

            if not derniere_execution:
                return {
                    "doit_executer": True,
                    "raison": "Pas de date de création trouvée",
                    "derniere_execution": None,
                    "nb_offres_recentes": len(offres_recentes),
                }

            # Vérifier si c'est dans les 24 dernières heures
            maintenant = datetime.now()
            if isinstance(derniere_execution, str):
                derniere_execution = datetime.fromisoformat(derniere_execution)

            delta = maintenant - derniere_execution

            # Compter les offres des 24 dernières heures
            stats_24h = await self.offres_repo.get_collection_stats()

            if delta <= timedelta(hours=24):
                return {
                    "doit_executer": False,
                    "raison": f"Données récentes trouvées (il y a {delta.total_seconds()/3600:.1f}h)",
                    "derniere_execution": derniere_execution,
                    "nb_offres_24h": stats_24h.get("total_offres", 0),
                }
            else:
                return {
                    "doit_executer": True,
                    "raison": f"Données obsolètes (il y a {delta.days} jours)",
                    "derniere_execution": derniere_execution,
                    "nb_offres_24h": stats_24h.get("total_offres", 0),
                }

        except Exception as e:
            logger.error(f"Erreur vérification dernière exécution: {e}")
            return {
                "doit_executer": True,
                "raison": f"Erreur vérification: {e}",
                "derniere_execution": None,
                "nb_offres_recentes": 0,
            }

    async def verifier_derniere_analyse_competences(self) -> dict[str, Any]:
        """
        Vérifie si l'analyse des compétences a été effectuée dans les 24 dernières heures

        Returns:
            Dict contenant le statut et les informations de la dernière analyse
        """
        try:
            # Chercher la dernière exécution de l'analyse des compétences
            derniere_execution = await self.db.pipeline_executions.find_one(
                {"type": "analyse_competences"}
            )

            if not derniere_execution:
                return {
                    "doit_analyser": True,
                    "raison": "Aucune analyse de compétences précédente trouvée",
                    "derniere_analyse": None,
                }

            derniere_analyse = derniere_execution.get("derniere_execution")
            if not derniere_analyse:
                return {
                    "doit_analyser": True,
                    "raison": "Date d'analyse manquante",
                    "derniere_analyse": None,
                }

            # Vérifier si c'est dans les 24 dernières heures
            maintenant = datetime.now()
            if isinstance(derniere_analyse, str):
                derniere_analyse = datetime.fromisoformat(derniere_analyse)

            delta = maintenant - derniere_analyse

            if delta <= timedelta(hours=24):
                return {
                    "doit_analyser": False,
                    "raison": f"Analyse récente trouvée (il y a {delta.total_seconds()/3600:.1f}h)",
                    "derniere_analyse": derniere_analyse,
                }
            else:
                return {
                    "doit_analyser": True,
                    "raison": f"Analyse obsolète (il y a {delta.days} jours)",
                    "derniere_analyse": derniere_analyse,
                }

        except Exception as e:
            logger.error(f"Erreur vérification dernière analyse: {e}")
            return {
                "doit_analyser": True,
                "raison": f"Erreur vérification: {e}",
                "derniere_analyse": None,
            }

    async def verifier_dernieres_statistiques(self) -> dict[str, Any]:
        """
        Vérifie si les statistiques ont été générées dans les 24 dernières heures

        Returns:
            Dict contenant le statut et les informations des dernières statistiques
        """
        try:
            # Chercher la dernière exécution des statistiques
            derniere_execution = await self.db.pipeline_executions.find_one(
                {"type": "statistiques"}
            )

            if not derniere_execution:
                return {
                    "doit_generer": True,
                    "raison": "Aucune statistique précédente trouvée",
                    "derniere_generation": None,
                }

            derniere_generation = derniere_execution.get("derniere_execution")
            if not derniere_generation:
                return {
                    "doit_generer": True,
                    "raison": "Date de génération manquante",
                    "derniere_generation": None,
                }

            # Vérifier si c'est dans les 24 dernières heures
            maintenant = datetime.now()
            if isinstance(derniere_generation, str):
                derniere_generation = datetime.fromisoformat(derniere_generation)

            delta = maintenant - derniere_generation

            if delta <= timedelta(hours=24):
                return {
                    "doit_generer": False,
                    "raison": f"Statistiques récentes trouvées (il y a {delta.total_seconds()/3600:.1f}h)",
                    "derniere_generation": derniere_generation,
                }
            else:
                return {
                    "doit_generer": True,
                    "raison": f"Statistiques obsolètes (il y a {delta.days} jours)",
                    "derniere_generation": derniere_generation,
                }

        except Exception as e:
            logger.error(f"Erreur vérification dernières statistiques: {e}")
            return {
                "doit_generer": True,
                "raison": f"Erreur vérification: {e}",
                "derniere_generation": None,
            }

    async def collecter_offres(self, max_offres: int | None = None) -> list[dict]:
        """
        Collecte les offres d'emploi M1805 via l'API France Travail

        Args:
            max_offres: Limite optionnelle du nombre d'offres

        Returns:
            Liste des offres collectées
        """
        logger.info(f"Début collecte offres {self.code_rome}")

        try:
            offres = self.api_client.collecter_offres_par_code_rome(
                self.code_rome, max_offres=max_offres
            )

            logger.info(f"{len(offres)} offres collectées")
            return offres

        except Exception as e:
            logger.error(f"Erreur collecte offres: {e}")
            return []

    async def convertir_et_sauvegarder_offres(self, offres_api: list[dict]) -> int:
        """
        Convertit les offres API en modèles MongoDB et les sauvegarde

        Args:
            offres_api: Liste des offres brutes de l'API

        Returns:
            Nombre d'offres sauvegardées
        """
        logger.info("Conversion et sauvegarde des offres dans MongoDB")

        offres_converties = []
        erreurs_conversion = 0

        for offre_api in offres_api:
            try:
                # Convertir l'offre API en modèle MongoDB
                offre_modele = await self._convertir_offre_api_vers_modele(offre_api)
                offres_converties.append(offre_modele)

            except Exception as e:
                erreurs_conversion += 1
                logger.warning(
                    f"Erreur conversion offre {offre_api.get('id', 'N/A')}: {e}"
                )

        if erreurs_conversion > 0:
            logger.warning(f"{erreurs_conversion} offres non converties")

        # Sauvegarde en lot dans MongoDB avec déduplication
        if offres_converties:
            logger.info(f"Tentative de sauvegarde de {len(offres_converties)} offres")
            nb_sauvegardees = await self.offres_repo.insert_many_offres(
                offres_converties
            )

            doublons = len(offres_converties) - nb_sauvegardees
            if doublons > 0:
                logger.info(
                    f"{nb_sauvegardees} nouvelles offres sauvegardées, {doublons} doublons ignorés"
                )
            else:
                logger.info(f"{nb_sauvegardees} offres sauvegardées dans MongoDB")

            return nb_sauvegardees
        else:
            logger.warning("Aucune offre à sauvegarder")
            return 0

    async def _convertir_offre_api_vers_modele(
        self, offre_api: dict
    ) -> OffreEmploiModel:
        """
        Convertit une offre API en modèle OffreEmploiModel pour MongoDB
        PRÉSERVE TOUS les champs de l'API France Travail sans perte de données

        Args:
            offre_api: Offre brute de l'API France Travail

        Returns:
            Modèle OffreEmploiModel avec TOUTES les données de l'API
        """
        # COPIE INTÉGRALE de l'offre API - aucune perte de données
        donnees_api_completes = dict(offre_api)  # Copie complète

        # Extraction sélective pour les champs spéciaux du modèle normalisé
        return OffreEmploiModel(
            # Identifiants et base
            source_id=str(offre_api.get("id", "")),
            intitule=offre_api.get("intitule", ""),
            description=offre_api.get("description", ""),
            # Dates avec gestion des formats
            date_creation=self._parse_date_api(offre_api.get("dateCreation")),
            date_mise_a_jour=self._parse_date_api(offre_api.get("dateActualisation")),
            # DONNÉES API COMPLÈTES - Conservation intégrale
            donnees_api_originales=donnees_api_completes,
            # Entreprise (extraction pour compatibilité)
            entreprise={
                "nom": offre_api.get("entreprise", {}).get("nom", ""),
                "description": offre_api.get("entreprise", {}).get("description", ""),
                "logo": offre_api.get("entreprise", {}).get("logo", ""),
                "url": offre_api.get("entreprise", {}).get("url", ""),
                "entrepriseAdaptee": offre_api.get("entreprise", {}).get(
                    "entrepriseAdaptee"
                ),
            },
            # Localisation complète avec coordonnées GPS
            localisation={
                "libelle": offre_api.get("lieuTravail", {}).get("libelle", ""),
                "latitude": offre_api.get("lieuTravail", {}).get("latitude"),
                "longitude": offre_api.get("lieuTravail", {}).get("longitude"),
                "codePostal": offre_api.get("lieuTravail", {}).get("codePostal", ""),
                "commune": offre_api.get("lieuTravail", {}).get("commune", ""),
                "departement": (
                    offre_api.get("lieuTravail", {}).get("codePostal", "")[:2]
                    if offre_api.get("lieuTravail", {}).get("codePostal")
                    else ""
                ),
            },
            # Contrat complet
            contrat={
                "type": offre_api.get("typeContrat", ""),
                "typeLibelle": offre_api.get("typeContratLibelle", ""),
                "natureContrat": offre_api.get("natureContrat", ""),
                "experienceExige": offre_api.get("experienceExige", ""),
                "experienceLibelle": offre_api.get("experienceLibelle", ""),
                "experienceCommentaire": offre_api.get("experienceCommentaire", ""),
                "dureeTravailLibelle": offre_api.get("dureeTravailLibelle", ""),
                "dureeTravailLibelleConverti": offre_api.get(
                    "dureeTravailLibelleConverti", ""
                ),
                "alternance": offre_api.get("alternance", False),
            },
            # Codes et métier
            rome_code=offre_api.get("romeCode", self.code_rome),
            rome_libelle=offre_api.get("romeLibelle", ""),
            appellation_libelle=offre_api.get("appellationlibelle", ""),
            # Secteur d'activité
            code_naf=offre_api.get("codeNAF", ""),
            secteur_activite=offre_api.get("secteurActivite", ""),
            secteur_activite_libelle=offre_api.get("secteurActiviteLibelle", ""),
            # Qualification
            qualification_code=offre_api.get("qualificationCode", ""),
            qualification_libelle=offre_api.get("qualificationLibelle", ""),
            # Salaire complet
            salaire=offre_api.get("salaire", {}),
            # Formations, langues, permis, compétences (listes complètes)
            formations=offre_api.get("formations", []),
            langues=offre_api.get("langues", []),
            permis=offre_api.get("permis", []),
            competences_requises=offre_api.get("competences", []),
            qualites_professionnelles=offre_api.get("qualitesProfessionnelles", []),
            outils_bureautiques=offre_api.get("outilsBureautiques", ""),
            # Contact et agence
            contact=offre_api.get("contact", {}),
            agence=offre_api.get("agence", {}),
            # Métadonnées étendues
            nombre_postes=offre_api.get("nombrePostes", 1),
            accessible_th=offre_api.get("accessibleTH", False),
            deplacement_code=offre_api.get("deplacementCode", ""),
            deplacement_libelle=offre_api.get("deplacementLibelle", ""),
            tranche_effectif_etab=offre_api.get("trancheEffectifEtab", ""),
            entreprise_adaptee=offre_api.get("entrepriseAdaptee", False),
            employeur_handi_engage=offre_api.get("employeurHandiEngage", False),
            # Origine et contexte
            origine_offre=offre_api.get("origineOffre", {}),
            offres_manque_candidats=offre_api.get("offresManqueCandidats", False),
            contexte_travail=offre_api.get("contexteTravail", {}),
            complement_exercice=offre_api.get("complementExercice", ""),
            condition_exercice=offre_api.get("conditionExercice", ""),
            # Compétences (à analyser plus tard)
            competences_extraites=[],
            # Métadonnées système
            code_rome=self.code_rome,
            source="france_travail_api",
            traite=False,
        )

    def _parse_date_api(self, date_str: str | None) -> datetime | None:
        """
        Parse les dates de l'API France Travail

        Args:
            date_str: Date sous forme de chaîne

        Returns:
            DateTime parsé ou None
        """
        if not date_str:
            return None

        try:
            # Format API France Travail: "2024-10-15T10:30:00.000Z"
            if "T" in date_str:
                date_str = (
                    date_str.split("T")[0] + "T" + date_str.split("T")[1].split(".")[0]
                )
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(date_str)
        except Exception as e:
            logger.warning(f"Erreur parsing date '{date_str}': {e}")
            return datetime.now()

    async def analyser_competences_mongodb(
        self, limite_offres: int | None = None, toutes_offres: bool = True
    ) -> dict[str, Any]:
        """
        Analyse les compétences des offres stockées dans MongoDB

        Args:
            limite_offres: Nombre max d'offres à analyser
            toutes_offres: Si True, analyse toutes les offres (pour time series)
                          Si False, seulement les 30 derniers jours

        Returns:
            Résultats de l'analyse
        """
        logger.info("Début analyse des compétences depuis MongoDB")

        # Choix du scope d'analyse
        if toutes_offres:
            logger.info(
                "🕐 Analyse de TOUTES les offres (séries temporelles long terme)"
            )
            offres_non_traitees = await self.offres_repo.get_toutes_offres(
                limit=limite_offres or 10000
            )
        else:
            logger.info("🕐 Analyse des offres récentes (30 derniers jours)")
            offres_non_traitees = await self.offres_repo.get_offres_recentes(
                jours=30, limit=limite_offres or 1000
            )

        if not offres_non_traitees:
            logger.warning("Aucune offre à analyser dans MongoDB")
            return {"nb_offres_analysees": 0, "competences_detectees": {}}

        logger.info(f"Analyse de {len(offres_non_traitees)} offres")

        # Convertir les offres MongoDB en format pour l'analyzer
        offres_pour_analyse = []
        for offre in offres_non_traitees:
            offres_pour_analyse.append(
                {
                    "id": offre.get("source_id"),
                    "intitule": offre.get("intitule", ""),
                    "description": offre.get("description", ""),
                }
            )

        # Analyser avec l'analyzer existant
        resultats = self.analyzer.analyser_offres(offres_pour_analyse, verbose=True)

        # Sauvegarder les compétences détectées en MongoDB
        await self._sauvegarder_competences_detectees(resultats)

        # Mettre à jour les offres avec les compétences
        await self._mettre_a_jour_offres_avec_competences(resultats)

        # Marquer la dernière exécution de l'analyse des compétences
        await self.db.pipeline_executions.replace_one(
            {"type": "analyse_competences"},
            {
                "type": "analyse_competences",
                "derniere_execution": datetime.now(),
                "nb_offres_analysees": len(offres_non_traitees),
            },
            upsert=True,
        )

        logger.info("Analyse des compétences terminée")
        return resultats

    async def _sauvegarder_competences_detectees(self, resultats: dict[str, Any]):
        """
        Sauvegarde les compétences détectées dans la collection competences_detections

        Args:
            resultats: Résultats de l'analyse des compétences
        """
        detections = []

        for offre_id, competences in resultats.get("competences_par_offre", {}).items():
            for competence in competences:
                detection = {
                    "offre_id": offre_id,
                    "competence": competence.get("nom", ""),
                    "methode_detection": "nlp",  # Méthode utilisée par l'analyzer
                    "confiance": competence.get("score", 1.0),
                    "contexte": competence.get("contexte", ""),
                    "date_detection": datetime.now(),
                }
                detections.append(detection)

        if detections:
            # Insérer dans la collection competences_detections
            collection = self.db.competences_detections
            await collection.insert_many(detections)
            logger.info(f"{len(detections)} détections de compétences sauvegardées")

    async def _mettre_a_jour_offres_avec_competences(self, resultats: dict[str, Any]):
        """
        Met à jour les offres avec les compétences détectées

        Args:
            resultats: Résultats de l'analyse
        """
        for offre_id, competences in resultats.get("competences_par_offre", {}).items():
            competences_noms = [comp.get("nom", "") for comp in competences]

            # Mettre à jour l'offre dans MongoDB
            await self.offres_repo.collection.update_one(
                {"source_id": offre_id},
                {
                    "$set": {
                        "competences_extraites": competences_noms,
                        "traite": True,
                        "date_traitement": datetime.now(),
                    }
                },
            )

    async def generer_statistiques(self) -> dict[str, Any]:
        """
        Génère les statistiques complètes depuis MongoDB

        Returns:
            Statistiques complètes
        """
        logger.info("Génération des statistiques MongoDB")

        # Statistiques générales
        stats_collection = await self.offres_repo.get_collection_stats()

        # Top compétences
        pipeline_top_competences = [
            {"$unwind": "$competences_extraites"},
            {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20},
        ]

        cursor = self.offres_repo.collection.aggregate(pipeline_top_competences)
        top_competences = await cursor.to_list(length=20)

        # Évolution temporelle (derniers 30 jours)
        stats_temporelles = await self.offres_repo.get_stats_temporelles(groupby="day")

        statistiques = {
            "periode_analysee": datetime.now().strftime("%Y-%m"),
            "date_analyse": datetime.now(),
            "nb_offres_analysees": stats_collection.get("total_offres", 0),
            "top_competences": [
                {
                    "competence": item["_id"],
                    "nb_occurrences": item["count"],
                    "pourcentage": round(
                        item["count"] / stats_collection.get("total_offres", 1) * 100, 2
                    ),
                }
                for item in top_competences
            ],
            "evolution_temporelle": stats_temporelles,
            "repartition_mensuelle": stats_collection.get("repartition_mensuelle", []),
        }

        # Sauvegarder les statistiques dans MongoDB
        await self.stats_repo.collection_stats.replace_one(
            {"periode_analysee": statistiques["periode_analysee"]},
            statistiques,
            upsert=True,
        )

        # Marquer la dernière exécution des statistiques
        await self.db.pipeline_executions.replace_one(
            {"type": "statistiques"},
            {
                "type": "statistiques",
                "derniere_execution": datetime.now(),
                "nb_offres_analysees": statistiques["nb_offres_analysees"],
            },
            upsert=True,
        )

        logger.info("Statistiques générées et sauvegardées")
        return statistiques

    async def executer_pipeline_complet(
        self,
        max_offres: int | None = None,
        forcer_execution: bool = False,
        forcer_analyses: bool = False,
    ) -> dict[str, Any]:
        """
        Exécute le pipeline complet MongoDB

        Args:
            max_offres: Limite d'offres à collecter
            forcer_execution: Ignorer la vérification des 24h pour la collecte
            forcer_analyses: Ignorer la vérification des 24h pour analyses et stats

        Returns:
            Résultats complets du pipeline
        """
        start_time = datetime.now()
        logger.info(f"🚀 Début pipeline MongoDB M1805 - Max offres: {max_offres}")

        try:
            # Initialiser la connexion MongoDB
            if not await self.init_database_connection():
                raise Exception("Impossible d'initialiser MongoDB")

            # Vérifier la dernière exécution
            if not forcer_execution:
                verification = await self.verifier_derniere_execution()
                if not verification["doit_executer"]:
                    logger.info(f"Pipeline ignoré: {verification['raison']}")
                    return {
                        "success": True,
                        "skipped": True,
                        "reason": verification["raison"],
                        "derniere_execution": verification["derniere_execution"],
                    }

            # 1. Collecte des offres
            offres_api = await self.collecter_offres(max_offres)
            if not offres_api:
                raise Exception("Aucune offre collectée")

            # 2. Conversion et sauvegarde
            nb_sauvegardees = await self.convertir_et_sauvegarder_offres(offres_api)

            # 3. Analyse des compétences (avec vérification 24h)
            verification_analyse = await self.verifier_derniere_analyse_competences()
            if verification_analyse["doit_analyser"] or forcer_analyses:
                logger.info("🧠 Début analyse des compétences")
                resultats_analyse = await self.analyser_competences_mongodb()
            else:
                logger.info(
                    f"⏭️ Analyse des compétences ignorée: {verification_analyse['raison']}"
                )
                resultats_analyse = {
                    "nb_offres_analysees": 0,
                    "competences_detectees": {},
                    "skipped": True,
                }

            # 4. Génération des statistiques (avec vérification 24h)
            verification_stats = await self.verifier_dernieres_statistiques()
            if verification_stats["doit_generer"] or forcer_analyses:
                logger.info("📊 Début génération des statistiques")
                statistiques = await self.generer_statistiques()
            else:
                logger.info(
                    f"⏭️ Génération des statistiques ignorée: {verification_stats['raison']}"
                )
                # Récupérer les dernières statistiques existantes
                dernieres_stats = await self.stats_repo.collection_stats.find_one(
                    {}, sort=[("date_analyse", -1)]
                )
                statistiques = (
                    dernieres_stats
                    if dernieres_stats
                    else {"top_competences": [], "skipped": True}
                )

            # Résultats finaux
            duree = datetime.now() - start_time
            resultats = {
                "success": True,
                "skipped": False,
                "duree_execution": str(duree),
                "nb_offres_collectees": len(offres_api),
                "nb_offres_sauvegardees": nb_sauvegardees,
                "nb_offres_analysees": resultats_analyse.get("nb_offres_analysees", 0),
                "nb_competences_detectees": len(
                    resultats_analyse.get("competences_detectees", {})
                ),
                "top_competences": statistiques.get("top_competences", [])[:10],
                "analyse_competences_skipped": resultats_analyse.get("skipped", False),
                "statistiques_skipped": statistiques.get("skipped", False),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Pipeline terminé avec succès en {duree}")
            return resultats

        except Exception as e:
            logger.error(f"❌ Erreur pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        # Note: Fermeture gérée par main.py pour éviter la double fermeture

    async def verifier_collecte_recente(
        self, heures_limite: int = 24
    ) -> dict[str, Any]:
        """
        Vérifie s'il y a eu une collecte récente dans MongoDB

        Args:
            heures_limite: Nombre d'heures pour considérer une collecte comme récente

        Returns:
            Dict avec informations sur la dernière collecte
        """
        try:
            from datetime import timedelta

            # Assurer la connexion MongoDB
            if not await self.init_database_connection():
                return {"doit_collecter": True, "raison": "Pas de connexion MongoDB"}

            # Chercher la collecte la plus récente
            dernier_document = await self.offres_repo.collection.find_one(
                sort=[("date_collecte", -1)]
            )

            if not dernier_document:
                return {"doit_collecter": True, "raison": "Aucune donnée en base"}

            date_limite = datetime.now() - timedelta(hours=heures_limite)
            date_collecte = dernier_document.get("date_collecte")

            if not date_collecte or date_collecte < date_limite:
                return {
                    "doit_collecter": True,
                    "raison": f"Dernière collecte trop ancienne ({date_collecte})",
                    "date_collecte": date_collecte,
                }

            # Compter les offres récentes
            nb_offres_recentes = await self.offres_repo.collection.count_documents(
                {"date_collecte": {"$gte": date_limite}}
            )

            return {
                "doit_collecter": False,
                "raison": f"Collecte récente trouvée ({nb_offres_recentes} offres)",
                "date_collecte": date_collecte,
                "nb_offres": nb_offres_recentes,
            }

        except Exception as e:
            self.logger.warning(f"Erreur vérification collecte récente: {e}")
            return {"doit_collecter": True, "raison": "Erreur vérification"}

    async def obtenir_statistiques_mongodb(self) -> dict[str, Any]:
        """
        Obtient les statistiques complètes depuis MongoDB

        Returns:
            Dict avec toutes les statistiques disponibles
        """
        try:
            # Assurer la connexion MongoDB
            if not await self.init_database_connection():
                return {"error": "Pas de connexion MongoDB"}

            # Statistiques des offres
            nb_offres_total = await self.offres_repo.collection.count_documents({})
            nb_offres_traitees = await self.offres_repo.collection.count_documents(
                {"traite": True}
            )

            # Dernière collecte
            derniere_collecte = await self.offres_repo.collection.find_one(
                sort=[("date_collecte", -1)]
            )

            # Statistiques des compétences
            nb_competences_total = (
                await self.competences_repo.collection.count_documents({})
            )
            nb_detections_total = await self.db.competences_detections.count_documents(
                {}
            )

            # Top compétences
            pipeline_top_competences = [
                {"$unwind": "$competences_extraites"},
                {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5},
            ]
            cursor = self.offres_repo.collection.aggregate(pipeline_top_competences)
            top_competences = await cursor.to_list(length=5)

            # Répartition par département (top 5)
            pipeline_dept = [
                {"$group": {"_id": "$localisation.departement", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5},
            ]
            cursor_dept = self.offres_repo.collection.aggregate(pipeline_dept)
            top_departements = await cursor_dept.to_list(length=5)

            stats = {
                "code_rome": "M1805",
                "nb_offres_total": nb_offres_total,
                "nb_offres_traitees": nb_offres_traitees,
                "nb_competences_total": nb_competences_total,
                "nb_detections_total": nb_detections_total,
                "derniere_collecte": (
                    derniere_collecte.get("date_collecte")
                    if derniere_collecte
                    else None
                ),
                "top_competences": [
                    {"competence": item["_id"], "occurrences": item["count"]}
                    for item in top_competences
                    if item["_id"]
                ],
                "top_departements": [
                    {"departement": item["_id"], "offres": item["count"]}
                    for item in top_departements
                    if item["_id"]
                ],
                "stockage": "MongoDB",
                "version_pipeline": "MongoDB v2.0",
            }

            return stats

        except Exception as e:
            self.logger.error(f"Erreur obtention statistiques MongoDB: {e}")
            return {
                "code_rome": "M1805",
                "nb_offres_total": 0,
                "nb_competences_total": 0,
                "stockage": "MongoDB (erreur)",
                "error": str(e),
            }


# Fonctions d'interface pour compatibilité
async def run_pipeline_mongodb(
    max_offres: int | None = None, forcer_execution: bool = False
) -> dict[str, Any]:
    """
    Lance le pipeline MongoDB M1805

    Args:
        max_offres: Limite d'offres
        forcer_execution: Ignorer la vérification 24h

    Returns:
        Résultats du pipeline
    """
    pipeline = PipelineMongoDBM1805()
    return await pipeline.executer_pipeline_complet(max_offres, forcer_execution)


def run_pipeline_mongodb_sync(
    max_offres: int | None = None, forcer_execution: bool = False
) -> dict[str, Any]:
    """
    Version synchrone du pipeline MongoDB (wrapper)

    Args:
        max_offres: Limite d'offres
        forcer_execution: Ignorer la vérification 24h

    Returns:
        Résultats du pipeline
    """
    return asyncio.run(run_pipeline_mongodb(max_offres, forcer_execution))


if __name__ == "__main__":
    # Test du pipeline MongoDB
    import sys

    max_offres = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    resultats = run_pipeline_mongodb_sync(max_offres=max_offres, forcer_execution=True)

    print("\n" + "=" * 60)
    print("🎯 RÉSULTATS PIPELINE MONGODB M1805")
    print("=" * 60)

    if resultats.get("success"):
        print(f"✅ Succès - Durée: {resultats.get('duree_execution')}")
        print(f"📊 Offres collectées: {resultats.get('nb_offres_collectees')}")
        print(f"💾 Offres sauvegardées: {resultats.get('nb_offres_sauvegardees')}")
        print(f"🧠 Offres analysées: {resultats.get('nb_offres_analysees')}")
        print(f"🔍 Compétences détectées: {resultats.get('nb_competences_detectees')}")

        if resultats.get("top_competences"):
            print("\n🏆 Top 5 compétences:")
            for i, comp in enumerate(resultats["top_competences"][:5], 1):
                print(
                    f"   {i}. {comp['competence']} - {comp['nb_occurrences']} occurrences"
                )
    else:
        print(f"❌ Échec: {resultats.get('error')}")
