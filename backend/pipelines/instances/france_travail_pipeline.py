"""
France Travail Pipeline - Pipeline configuré pour France Travail M1805
Instance complète du pipeline avec collecteur, orchestrateur et configuration
"""

import asyncio
from typing import Any

from ..base.pipeline_orchestrator import PipelineOrchestrator
from ..base.stats_generator import StatsGenerator
from ..sources.france_travail_collector import FranceTravailCollector
from ...database.connection import DatabaseConnection
from ...tools.logging_config import get_logger

logger = get_logger(__name__)


class FranceTravailPipeline:
    """
    Pipeline complet pour France Travail M1805
    Orchestre la collecte, l'analyse et les statistiques pour les offres France Travail
    """
    
    def __init__(
        self, 
        code_rome: str = "M1805",
        database_connection: DatabaseConnection | None = None
    ):
        """
        Initialise le pipeline France Travail
        
        Args:
            code_rome: Code ROME à traiter (défaut: M1805 - Études et développement informatique)
            database_connection: Connexion MongoDB (optionnel)
        """
        self.code_rome = code_rome
        
        # Composants du pipeline
        self.collector = FranceTravailCollector(code_rome)
        self.stats_generator = StatsGenerator(source_name="france_travail")
        self.orchestrator = PipelineOrchestrator(
            pipeline_name=f"france_travail_{code_rome.lower()}",
            data_collector=self.collector,
            stats_generator=self.stats_generator,
            database_connection=database_connection
        )
        
        logger.info(f"Pipeline France Travail {code_rome} initialisé")
    
    async def execute_full_pipeline(
        self,
        max_jobs: int | None = None,
        force_collection: bool = False,
        force_analysis: bool = False, 
        force_stats: bool = False
    ) -> dict[str, Any]:
        """
        Exécute le pipeline complet France Travail
        
        Args:
            max_jobs: Limite d'offres à collecter
            force_collection: Forcer la collecte même si récente
            force_analysis: Forcer l'analyse même si récente
            force_stats: Forcer les stats même si récentes
            
        Returns:
            Résultats complets du pipeline
        """
        logger.info(f"Lancement pipeline France Travail {self.code_rome}")
        
        return await self.orchestrator.execute_complete_pipeline(
            max_jobs=max_jobs,
            force_collection=force_collection,
            force_analysis=force_analysis,
            force_stats=force_stats
        )
    
    async def execute_collection_only(
        self, 
        max_jobs: int | None = None
    ) -> dict[str, Any]:
        """
        Exécute seulement la collecte des offres
        
        Args:
            max_jobs: Limite d'offres à collecter
            
        Returns:
            Résultats de la collecte
        """
        logger.info(f"Collecte seule France Travail {self.code_rome}")
        
        # Initialiser la DB
        if not await self.orchestrator.init_database():
            return {
                "success": False,
                "error": "Impossible d'initialiser la base de données"
            }
        
        try:
            # Exécuter la collecte optimisée
            results = await self.collector.collect_and_save_jobs_optimized(max_jobs)
            return {
                "success": True,
                "pipeline_name": self.orchestrator.pipeline_name,
                "mode": "collection_optimized",
                "collection": results,
            }
        finally:
            await self.orchestrator.close_database()
    
    async def execute_optimized_collection(
        self, 
        max_jobs: int | None = None
    ) -> dict[str, Any]:
        """
        Exécute la nouvelle collecte optimisée avec filtrage intelligent
        
        Fonctionnalités :
        - Pas de filtre 30 jours (toutes les offres API)
        - Déduplication automatique
        - Filtrage par compétences en temps réel
        - Gestion automatique des clôtures
        
        Args:
            max_jobs: Limite d'offres à collecter
            
        Returns:
            Résultats détaillés de la collecte optimisée
        """
        logger.info(f"🚀 Collecte optimisée France Travail {self.code_rome}")
        
        # Initialiser la DB
        if not await self.orchestrator.init_database():
            return {
                "success": False,
                "error": "Impossible d'initialiser la base de données"
            }
        
        try:
            # Exécuter la collecte optimisée
            results = await self.collector.collect_and_save_jobs_optimized(max_jobs)
            
            logger.info(
                f"✅ Collecte optimisée terminée: "
                f"{results.get('nb_sauvegardees', 0)} nouvelles offres avec compétences"
            )
            
            return {
                "success": True,
                "pipeline_name": self.orchestrator.pipeline_name,
                "mode": "optimized_collection",
                "collection": results,
                "summary": {
                    "nouvelles_offres": results.get('nb_sauvegardees', 0),
                    "doublons_evites": results.get('nb_doublons', 0),
                    "sans_competences": results.get('nb_filtrees', 0),
                    "offres_cloturees": results.get('nb_clôturees', 0),
                }
            }
        finally:
            await self.orchestrator.close_database()
    
    async def get_pipeline_stats(self) -> dict[str, Any]:
        """
        Obtient les statistiques du pipeline France Travail
        
        Returns:
            Statistiques du pipeline
        """
        try:
            if not await self.orchestrator.init_database():
                return {"error": "Impossible d'initialiser la base de données"}
            
            # Stats du collecteur
            collector_stats = await self.collector.get_collection_stats()
            
            # Stats des vérifications de throttling
            collection_check = await self.orchestrator.check_should_collect()
            analysis_check = await self.orchestrator.check_should_analyze()
            stats_check = await self.orchestrator.check_should_generate_stats()
            
            return {
                "pipeline_name": self.orchestrator.pipeline_name,
                "code_rome": self.code_rome,
                "source": self.collector.source_name,
                
                # Stats de collecte
                **collector_stats,
                
                # États des vérifications
                "should_collect": collection_check["should_execute"],
                "collection_reason": collection_check["reason"],
                "should_analyze": analysis_check["should_execute"], 
                "analysis_reason": analysis_check["reason"],
                "should_generate_stats": stats_check["should_execute"],
                "stats_reason": stats_check["reason"],
            }
            
        except Exception as e:
            logger.error(f"Erreur stats pipeline France Travail: {e}")
            return {
                "pipeline_name": self.orchestrator.pipeline_name,
                "error": str(e)
            }
        finally:
            await self.orchestrator.close_database()
    
    # === MÉTHODES DE COMPATIBILITÉ AVEC L'ANCIEN PIPELINE ===
    
    async def executer_pipeline_complet(
        self, 
        max_offres: int | None = None, 
        forcer_execution: bool = False,
        forcer_analyses: bool = False
    ) -> dict[str, Any]:
        """
        Méthode de compatibilité avec l'ancien PipelineMongoDBM1805
        
        Args:
            max_offres: Limite d'offres à collecter
            forcer_execution: Forcer la collecte
            forcer_analyses: Forcer analyses et stats
        
        Returns:
            Résultats du pipeline (format compatible avec l'ancien)
        """
        results = await self.execute_full_pipeline(
            max_jobs=max_offres,
            force_collection=forcer_execution,
            force_analysis=forcer_analyses,
            force_stats=forcer_analyses
        )
        
        # Adapter le format pour compatibilité
        collection = results.get("collection", {})
        statistics = results.get("statistics", {})
        
        return {
            "success": results.get("success", False),
            "skipped": collection.get("skipped", False),
            "duree_execution": results.get("duration", "0:00:00"),
            "nb_offres_collectees": collection.get("nb_offres_collectees", 0),
            "nb_offres_sauvegardees": collection.get("nb_nouvelles_offres", 0),
            "nb_offres_analysees": statistics.get("nb_offres_analysees", 0),
            "nb_competences_detectees": statistics.get("nb_competences_detectees", 0),
            "top_competences": statistics.get("top_competences", []),
            "statistiques_par_categorie": statistics.get("statistiques_par_categorie", {}),
            "collecte_skipped": collection.get("skipped", False),
            "analyse_competences_skipped": False,  # TODO: à implémenter
            "statistiques_skipped": statistics.get("skipped", False),
            "timestamp": results.get("timestamp", ""),
        }
    
    async def obtenir_statistiques_mongodb(self) -> dict[str, Any]:
        """
        Méthode de compatibilité pour obtenir les statistiques depuis MongoDB
        
        Returns:
            Statistiques formatées comme l'ancien pipeline
        """
        try:
            # Utiliser le générateur de statistiques
            if not self.stats_generator:
                return {"error": "StatsGenerator non configuré"}
            
            # Initialiser la base si nécessaire
            await self.orchestrator.init_database()
            
            # Obtenir les dernières statistiques
            latest_stats = await self.stats_generator.get_latest_statistics()
            
            if not latest_stats:
                # Générer des statistiques basiques
                if not self.orchestrator.offres_repo:
                    return {"error": "Repository non initialisé"}
                
                nb_offres_total = await self.orchestrator.offres_repo.collection.count_documents({
                    "source": "france_travail"
                })
                
                return {
                    "code_rome": self.code_rome,
                    "nb_offres_total": nb_offres_total,
                    "nb_offres_traitees": 0,
                    "nb_competences_total": 0,
                    "nb_detections_total": 0,
                    "derniere_collecte": None,
                    "top_competences": [],
                    "top_departements": [],
                    "stockage": "MongoDB",
                    "version_pipeline": "Modulaire v2.0",
                }
            
            # Adapter le format des statistiques
            return {
                "code_rome": self.code_rome,
                "nb_offres_total": latest_stats.get("nb_offres_analysees", 0),
                "nb_offres_traitees": latest_stats.get("nb_offres_analysees", 0),
                "nb_competences_total": latest_stats.get("nb_competences_detectees", 0),
                "nb_detections_total": 0,  # TODO: calculer
                "derniere_collecte": latest_stats.get("date_analyse"),
                "top_competences": [
                    {"competence": comp["competence"], "occurrences": comp["nb_occurrences"]}
                    for comp in latest_stats.get("top_competences", [])[:5]
                ],
                "top_departements": [],  # TODO: à implémenter
                "stockage": "MongoDB",
                "version_pipeline": "Modulaire v2.0",
            }
            
        except Exception as e:
            logger.error(f"Erreur obtention statistiques: {e}")
            return {
                "code_rome": self.code_rome,
                "nb_offres_total": 0,
                "nb_competences_total": 0,
                "stockage": "MongoDB (erreur)",
                "error": str(e),
            }
    
    async def verifier_collecte_recente(self, heures_limite: int = 24) -> dict[str, Any]:
        """
        Méthode de compatibilité pour vérifier la collecte récente
        
        Args:
            heures_limite: Nombre d'heures pour considérer une collecte comme récente
            
        Returns:
            Dict avec informations sur la dernière collecte
        """
        try:
            await self.orchestrator.init_database()
            
            # Utiliser la logique de vérification de l'orchestrateur
            check = await self.orchestrator.check_should_collect()
            
            return {
                "doit_collecter": check["should_execute"],
                "raison": check["reason"],
                "date_collecte": check.get("last_execution"),
                "nb_offres": 0  # TODO: calculer si nécessaire
            }
            
        except Exception as e:
            logger.warning(f"Erreur vérification collecte récente: {e}")
            return {
                "doit_collecter": True,
                "raison": f"Erreur vérification: {e}",
                "date_collecte": None,
                "nb_offres": 0
            }
    
    async def close_database_connection(self):
        """
        Méthode de compatibilité pour fermer les connexions
        (Géré automatiquement par l'orchestrateur)
        """
        if hasattr(self.orchestrator, 'close_database'):
            await self.orchestrator.close_database()


# Fonctions de compatibilité avec l'ancien système

async def run_france_travail_pipeline(
    max_offres: int | None = None,
    forcer_execution: bool = False
) -> dict[str, Any]:
    """
    Fonction de compatibilité avec l'ancien système
    
    Args:
        max_offres: Limite d'offres (ancien nom)
        forcer_execution: Forcer l'exécution complète
        
    Returns:
        Résultats du pipeline
    """
    pipeline = FranceTravailPipeline()
    
    return await pipeline.execute_full_pipeline(
        max_jobs=max_offres,
        force_collection=forcer_execution,
        force_analysis=forcer_execution,
        force_stats=forcer_execution
    )


def run_france_travail_pipeline_sync(
    max_offres: int | None = None,
    forcer_execution: bool = False
) -> dict[str, Any]:
    """
    Version synchrone pour compatibilité
    
    Args:
        max_offres: Limite d'offres
        forcer_execution: Forcer l'exécution
        
    Returns:
        Résultats du pipeline
    """
    return asyncio.run(run_france_travail_pipeline(max_offres, forcer_execution))


if __name__ == "__main__":
    # Test du nouveau pipeline
    import sys
    
    max_offres = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    force = len(sys.argv) > 2 and sys.argv[2].lower() == "force"
    
    async def test_pipeline():
        pipeline = FranceTravailPipeline()
        
        # Afficher les stats d'abord
        stats = await pipeline.get_pipeline_stats()
        print("\n📊 STATS PIPELINE FRANCE TRAVAIL:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Exécuter le pipeline
        print(f"\n🚀 EXÉCUTION PIPELINE (max: {max_offres}, force: {force})")
        results = await pipeline.execute_full_pipeline(
            max_jobs=max_offres,
            force_collection=force,
            force_analysis=force, 
            force_stats=force
        )
        
        # Afficher les résultats
        print("\n✅ RÉSULTATS:")
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"   {key}: {value}")
    
    asyncio.run(test_pipeline())