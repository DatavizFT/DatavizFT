"""
France Travail Collector - Collecteur spécialisé pour l'API France Travail
Implémentation concrète du collecteur pour les offres France Travail M1805
"""

from datetime import datetime
from typing import Any

from ..base.data_collector import BaseDataCollector
from ...clients.france_travail import FranceTravailAPIClient
from ...data import COMPETENCES_REFERENTIEL
from ...tools.logging_config import get_logger
from ...tools.competence_analyzer import CompetenceAnalyzer

logger = get_logger(__name__)


class FranceTravailCollector(BaseDataCollector):
    """
    Collecteur spécialisé pour l'API France Travail
    Gère la collecte des offres M1805 (Études et développement informatique)
    """
    
    def __init__(self, code_rome: str = "M1805", config: dict[str, Any] | None = None):
        """
        Initialise le collecteur France Travail
        
        Args:
            code_rome: Code ROME des offres à collecter (défaut: M1805)
            config: Configuration additionnelle
        """
        super().__init__("france_travail", config)
        
        self.code_rome = code_rome
        self.description = "Études et développement informatique"
        
        # Client API France Travail
        self.api_client = FranceTravailAPIClient()
        
        # Analyseur de compétences pour filtrage temps réel
        self.competence_analyzer = CompetenceAnalyzer(COMPETENCES_REFERENTIEL)
        
        logger.info(f"Collecteur France Travail initialisé - Code ROME: {code_rome}")
    
    async def collect_and_save_jobs_optimized(self, max_jobs: int | None = None, **kwargs) -> dict[str, Any]:
        """
        Collecte et sauvegarde intelligente avec filtrage avancé
        
        Nouvelle logique :
        1. Pas de filtre 30 jours
        2. Vérifie doublons (source_id)
        3. Ne sauve que les offres avec compétences
        4. Gère la clôture automatique des offres
        
        Returns:
            Résultats détaillés de la collecte optimisée
        """
        try:
            logger.info(f"🚀 Collecte France Travail optimisée - Code ROME: {self.code_rome}")
            
            # 1. Collecte brute depuis l'API (TOUTES les offres disponibles)
            raw_jobs = await self.collect_raw_jobs(max_jobs, **kwargs)
            
            if not raw_jobs:
                return {"success": True, "nb_collectees": 0, "nb_sauvegardees": 0, "nb_doublons": 0, "nb_filtrees": 0, "nb_clôturees": 0}
            
            logger.info(f"📊 {len(raw_jobs)} offres collectées depuis l'API France Travail")
            
            # 2. Récupération des source_id existants pour déduplication
            source_ids_api = {str(job.get("id", "")) for job in raw_jobs}
            source_ids_existants = await self.offres_repo.get_existing_source_ids(list(source_ids_api))
            
            # 3. Récupération des offres actives (sans date_cloture) pour gestion des clôtures
            offres_actives = await self.offres_repo.get_active_offers_by_source(self.source_name)
            source_ids_actifs = {offre["source_id"] for offre in offres_actives}
            
            # 4. Identification des offres à clôturer (actives mais plus dans l'API)
            source_ids_a_cloturer = source_ids_actifs - source_ids_api
            nb_clôturees = 0
            if source_ids_a_cloturer:
                nb_clôturees = await self.offres_repo.close_offers(list(source_ids_a_cloturer))
                logger.info(f"📝 {nb_clôturees} offres clôturées automatiquement")
            
            # 5. Filtrage et traitement des nouvelles offres
            nouvelles_offres = []
            nb_doublons = 0
            nb_filtrees = 0
            
            for raw_job in raw_jobs:
                source_id = str(raw_job.get("id", ""))
                
                # Ignorer les doublons
                if source_id in source_ids_existants:
                    nb_doublons += 1
                    continue
                
                # Vérifier si l'offre contient des compétences
                texte_offre = f"{raw_job.get('intitule', '')} {raw_job.get('description', '')}"
                competences_detectees = self.competence_analyzer.analyser_texte(texte_offre)
                
                # Ne garder que les offres avec compétences
                if not competences_detectees:
                    nb_filtrees += 1
                    continue
                
                # Convertir et enrichir l'offre
                try:
                    job_model = await self.convert_job_to_model(raw_job)
                    job_model.update({
                        "source": self.source_name,
                        "date_collecte": datetime.now(),
                        "traite": True,  # Déjà analysée
                        "competences_extraites": competences_detectees,
                    })
                    nouvelles_offres.append(job_model)
                    
                except Exception as e:
                    logger.warning(f"Erreur conversion offre {source_id}: {e}")
            
            # 6. Sauvegarde des nouvelles offres valides
            nb_sauvegardees = 0
            if nouvelles_offres:
                from ...models.mongodb.schemas import OffreEmploiModel
                
                offre_models = []
                for job_data in nouvelles_offres:
                    try:
                        offre_model = OffreEmploiModel(**job_data)
                        offre_models.append(offre_model)
                    except Exception as e:
                        logger.warning(f"Erreur création modèle: {e}")
                
                nb_sauvegardees = await self.offres_repo.insert_many_offres(offre_models)
            
            # 7. Résultats détaillés
            results = {
                "success": True,
                "source": self.source_name,
                "nb_collectees": len(raw_jobs),
                "nb_sauvegardees": nb_sauvegardees,
                "nb_doublons": nb_doublons,
                "nb_filtrees": nb_filtrees,  # Offres sans compétences
                "nb_clôturees": nb_clôturees,
            }
            
            logger.info(
                f"✅ Collecte optimisée terminée: {nb_sauvegardees} nouvelles offres, "
                f"{nb_doublons} doublons, {nb_filtrees} filtrées, {nb_clôturees} clôturées"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte optimisée {self.source_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def collect_raw_jobs(self, max_jobs: int | None = None, **kwargs) -> list[dict]:
        """
        Collecte les offres brutes depuis l'API France Travail
        
        Args:
            max_jobs: Limite du nombre d'offres
            **kwargs: Paramètres supplémentaires (ignorés pour France Travail)
            
        Returns:
            Liste des offres brutes de l'API France Travail
        """
        try:
            logger.info(f"🔍 Collecte France Travail - Code ROME: {self.code_rome}")
            
            # Utiliser le client API existant
            offres = self.api_client.collecter_offres_par_code_rome(
                self.code_rome, 
                max_offres=max_jobs
            )
            
            logger.info(f"📊 {len(offres)} offres collectées depuis France Travail")
            return offres
            
        except Exception as e:
            logger.error(f"Erreur collecte France Travail: {e}")
            return []
    
    def get_job_id(self, raw_job: dict) -> str:
        """
        Extrait l'ID unique de l'offre France Travail
        
        Args:
            raw_job: Offre brute de l'API France Travail
            
        Returns:
            ID unique de l'offre
        """
        return str(raw_job.get("id", ""))
    
    async def convert_job_to_model(self, raw_job: dict) -> dict:
        """
        Convertit une offre France Travail en modèle normalisé
        
        Args:
            raw_job: Offre brute de l'API France Travail
            
        Returns:
            Modèle d'offre normalisé pour MongoDB
        """
        # COPIE INTÉGRALE de l'offre API - aucune perte de données
        donnees_api_completes = dict(raw_job)
        
        # Extraction et normalisation des champs
        return {
            # Identifiants et base
            "source_id": str(raw_job.get("id", "")),
            "intitule": raw_job.get("intitule", ""),
            "description": raw_job.get("description", ""),
            
            # Dates avec parsing
            "date_creation": self._parse_date_api(raw_job.get("dateCreation")),
            "date_mise_a_jour": self._parse_date_api(raw_job.get("dateActualisation")),
            
            # DONNÉES API COMPLÈTES - Conservation intégrale  
            "donnees_api_originales": donnees_api_completes,
            
            # Entreprise (extraction pour compatibilité)
            "entreprise": {
                "nom": raw_job.get("entreprise", {}).get("nom", ""),
                "description": raw_job.get("entreprise", {}).get("description", ""),
                "logo": raw_job.get("entreprise", {}).get("logo", ""),
                "url": raw_job.get("entreprise", {}).get("url", ""),
                "entrepriseAdaptee": raw_job.get("entreprise", {}).get("entrepriseAdaptee"),
            },
            
            # Localisation complète avec coordonnées GPS
            "localisation": {
                "libelle": raw_job.get("lieuTravail", {}).get("libelle", ""),
                "latitude": raw_job.get("lieuTravail", {}).get("latitude"),
                "longitude": raw_job.get("lieuTravail", {}).get("longitude"), 
                "codePostal": raw_job.get("lieuTravail", {}).get("codePostal", ""),
                "commune": raw_job.get("lieuTravail", {}).get("commune", ""),
                "departement": (
                    raw_job.get("lieuTravail", {}).get("codePostal", "")[:2]
                    if raw_job.get("lieuTravail", {}).get("codePostal")
                    else ""
                ),
            },
            
            # Contrat complet
            "contrat": {
                "type": raw_job.get("typeContrat", ""),
                "typeLibelle": raw_job.get("typeContratLibelle", ""),
                "natureContrat": raw_job.get("natureContrat", ""),
                "experienceExige": raw_job.get("experienceExige", ""),
                "experienceLibelle": raw_job.get("experienceLibelle", ""),
                "experienceCommentaire": raw_job.get("experienceCommentaire", ""),
                "dureeTravailLibelle": raw_job.get("dureeTravailLibelle", ""),
                "dureeTravailLibelleConverti": raw_job.get("dureeTravailLibelleConverti", ""),
                "alternance": raw_job.get("alternance", False),
            },
            
            # Codes et métier
            "rome_code": raw_job.get("romeCode", self.code_rome),
            "rome_libelle": raw_job.get("romeLibelle", ""),
            "appellation_libelle": raw_job.get("appellationlibelle", ""),
            
            # Secteur d'activité
            "code_naf": raw_job.get("codeNAF", ""),
            "secteur_activite": raw_job.get("secteurActivite", ""),
            "secteur_activite_libelle": raw_job.get("secteurActiviteLibelle", ""),
            
            # Qualification
            "qualification_code": raw_job.get("qualificationCode", ""),
            "qualification_libelle": raw_job.get("qualificationLibelle", ""),
            
            # Salaire complet
            "salaire": raw_job.get("salaire", {}),
            
            # Formations, langues, permis, compétences (listes complètes)
            "formations": raw_job.get("formations", []),
            "langues": raw_job.get("langues", []),
            "permis": raw_job.get("permis", []),
            "competences_requises": raw_job.get("competences", []),
            "qualites_professionnelles": raw_job.get("qualitesProfessionnelles", []),
            "outils_bureautiques": raw_job.get("outilsBureautiques", ""),
            
            # Contact et agence
            "contact": raw_job.get("contact", {}),
            "agence": raw_job.get("agence", {}),
            
            # Métadonnées étendues
            "nombre_postes": raw_job.get("nombrePostes", 1),
            "accessible_th": raw_job.get("accessibleTH", False),
            "deplacement_code": raw_job.get("deplacementCode", ""),
            "deplacement_libelle": raw_job.get("deplacementLibelle", ""),
            "tranche_effectif_etab": raw_job.get("trancheEffectifEtab", ""),
            "entreprise_adaptee": raw_job.get("entrepriseAdaptee", False),
            "employeur_handi_engage": raw_job.get("employeurHandiEngage", False),
            
            # Origine et contexte
            "origine_offre": raw_job.get("origineOffre", {}),
            "offres_manque_candidats": raw_job.get("offresManqueCandidats", False),
            "contexte_travail": raw_job.get("contexteTravail", {}),
            "complement_exercice": raw_job.get("complementExercice", ""),
            "condition_exercice": raw_job.get("conditionExercice", ""),
            
            # Métadonnées système (ajoutées automatiquement par BaseDataCollector)
            "code_rome": self.code_rome,
        }
    
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