"""
Pipeline Orchestrator - Orchestrateur générique multi-sources
Coordonne l'exécution des pipelines avec logique de throttling 24h
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from .data_collector import BaseDataCollector
from .stats_generator import StatsGenerator
from ...database.connection import DatabaseConnection
from ...database.repositories import (
    CompetencesRepository, 
    OffresRepository, 
    StatsRepository
)
from ...tools.logging_config import get_logger

logger = get_logger(__name__)


class PipelineOrchestrator:
    """
    Orchestrateur générique pour pipelines multi-sources
    Gère la coordination, le throttling 24h et l'exécution des étapes
    """
    
    def __init__(
        self,
        pipeline_name: str,
        data_collector: BaseDataCollector,
        stats_generator: StatsGenerator | None = None,
        database_connection: DatabaseConnection | None = None
    ):
        """
        Initialise l'orchestrateur
        
        Args:
            pipeline_name: Nom unique du pipeline (ex: "france_travail_m1805")
            data_collector: Collecteur de données spécialisé
            database_connection: Connexion MongoDB (optionnel)
        """
        self.pipeline_name = pipeline_name
        self.data_collector = data_collector
        self.stats_generator = stats_generator
        
        # Connexion base de données
        self.db_connection = database_connection or DatabaseConnection()
        self.db: AsyncIOMotorDatabase | None = None
        
        # Repositories
        self.offres_repo: OffresRepository | None = None
        self.competences_repo: CompetencesRepository | None = None 
        self.stats_repo: StatsRepository | None = None
        
        logger.info(f"Orchestrateur {pipeline_name} initialisé")
    
    async def init_database(self) -> bool:
        """
        Initialise les connexions base de données
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Test de connexion
            if not await self.db_connection.connect():
                return False
            
            # Récupération de la DB
            self.db = self.db_connection.async_db
            
            # Initialisation des repositories
            self.offres_repo = OffresRepository(self.db)
            self.competences_repo = CompetencesRepository(self.db) 
            self.stats_repo = StatsRepository(self.db)
            
            # Configuration du collecteur et générateur de stats
            self.data_collector.set_database(self.db)
            if self.stats_generator:
                self.stats_generator.set_database(self.db)
            
            logger.info(f"[OK] Base de données initialisée pour {self.pipeline_name}")
            return True
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur init DB {self.pipeline_name}: {e}")
            return False
    
    async def close_database(self):
        """Ferme les connexions base de données"""
        try:
            if self.db_connection:
                await self.db_connection.close()
                logger.info(f"[DB] Connexions fermées pour {self.pipeline_name}")
        except Exception as e:
            logger.warning(f"Erreur fermeture DB {self.pipeline_name}: {e}")
    
    async def check_should_collect(self, hours_limit: int = 24) -> dict[str, Any]:
        """
        Vérifie si la collecte doit être exécutée (throttling)
        
        Args:
            hours_limit: Limite en heures pour considérer une collecte comme récente
            
        Returns:
            Dictionnaire avec should_execute et informations
        """
        try:
            # Vérifier la dernière collecte de cette source
            last_collection = await self.offres_repo.collection.find_one(
                {"source": self.data_collector.source_name},
                sort=[("date_collecte", -1)]
            )
            
            if not last_collection:
                return {
                    "should_execute": True,
                    "reason": f"Aucune collecte précédente pour {self.data_collector.source_name}",
                    "last_execution": None,
                }
            
            last_date = last_collection.get("date_collecte")
            if not last_date:
                return {
                    "should_execute": True,
                    "reason": "Date de collecte manquante",
                    "last_execution": None,
                }
            
            # Vérifier le délai
            now = datetime.now()
            if isinstance(last_date, str):
                last_date = datetime.fromisoformat(last_date)
            
            delta = now - last_date
            
            if delta <= timedelta(hours=hours_limit):
                return {
                    "should_execute": False,
                    "reason": f"Collecte récente (il y a {delta.total_seconds()/3600:.1f}h)",
                    "last_execution": last_date,
                    "hours_since_last": delta.total_seconds() / 3600,
                }
            else:
                return {
                    "should_execute": True,
                    "reason": f"Collecte obsolète (il y a {delta.days} jours {delta.seconds//3600}h)",
                    "last_execution": last_date,
                    "hours_since_last": delta.total_seconds() / 3600,
                }
                
        except Exception as e:
            logger.error(f"Erreur vérification collecte {self.pipeline_name}: {e}")
            return {
                "should_execute": True,
                "reason": f"Erreur vérification: {e}",
                "last_execution": None,
            }
    
    async def check_should_analyze(self, hours_limit: int = 24) -> dict[str, Any]:
        """
        Vérifie si l'analyse des compétences doit être exécutée
        
        Args:
            hours_limit: Limite en heures
            
        Returns:
            Dictionnaire avec should_execute et informations
        """
        try:
            # Chercher la dernière analyse pour ce pipeline
            last_analysis = await self.db.pipeline_executions.find_one(
                {
                    "pipeline_name": self.pipeline_name,
                    "type": "analyse_competences"
                },
                sort=[("derniere_execution", -1)]
            )
            
            if not last_analysis:
                return {
                    "should_execute": True,
                    "reason": f"Aucune analyse précédente pour {self.pipeline_name}",
                    "last_execution": None,
                }
            
            last_date = last_analysis.get("derniere_execution")
            if not last_date:
                return {
                    "should_execute": True,
                    "reason": "Date d'analyse manquante",
                    "last_execution": None,
                }
            
            # Vérifier le délai
            now = datetime.now()
            if isinstance(last_date, str):
                last_date = datetime.fromisoformat(last_date)
            
            delta = now - last_date
            
            if delta <= timedelta(hours=hours_limit):
                return {
                    "should_execute": False,
                    "reason": f"Analyse récente (il y a {delta.total_seconds()/3600:.1f}h)",
                    "last_execution": last_date,
                }
            else:
                return {
                    "should_execute": True,
                    "reason": f"Analyse obsolète (il y a {delta.days} jours)",
                    "last_execution": last_date,
                }
                
        except Exception as e:
            logger.error(f"Erreur vérification analyse {self.pipeline_name}: {e}")
            return {
                "should_execute": True,
                "reason": f"Erreur vérification: {e}",
                "last_execution": None,
            }
    
    async def check_should_generate_stats(self, hours_limit: int = 24) -> dict[str, Any]:
        """
        Vérifie si la génération de statistiques doit être exécutée
        
        Args:
            hours_limit: Limite en heures
            
        Returns:
            Dictionnaire avec should_execute et informations  
        """
        try:
            # Chercher la dernière génération pour ce pipeline
            last_stats = await self.db.pipeline_executions.find_one(
                {
                    "pipeline_name": self.pipeline_name,
                    "type": "statistiques"
                },
                sort=[("derniere_execution", -1)]
            )
            
            if not last_stats:
                return {
                    "should_execute": True,
                    "reason": f"Aucune statistique précédente pour {self.pipeline_name}",
                    "last_execution": None,
                }
            
            last_date = last_stats.get("derniere_execution")
            if not last_date:
                return {
                    "should_execute": True,
                    "reason": "Date de génération manquante",
                    "last_execution": None,
                }
            
            # Vérifier le délai
            now = datetime.now()
            if isinstance(last_date, str):
                last_date = datetime.fromisoformat(last_date)
            
            delta = now - last_date
            
            if delta <= timedelta(hours=hours_limit):
                return {
                    "should_execute": False,
                    "reason": f"Statistiques récentes (il y a {delta.total_seconds()/3600:.1f}h)",
                    "last_execution": last_date,
                }
            else:
                return {
                    "should_execute": True,
                    "reason": f"Statistiques obsolètes (il y a {delta.days} jours)",
                    "last_execution": last_date,
                }
                
        except Exception as e:
            logger.error(f"Erreur vérification stats {self.pipeline_name}: {e}")
            return {
                "should_execute": True,
                "reason": f"Erreur vérification: {e}",
                "last_execution": None,
            }
    
    async def execute_complete_pipeline(
        self,
        max_jobs: int | None = None,
        force_collection: bool = False,
        force_analysis: bool = False,
        force_stats: bool = False,
        **collect_kwargs
    ) -> dict[str, Any]:
        """
        Exécute le pipeline complet avec orchestration intelligente
        
        Args:
            max_jobs: Limite d'offres à collecter
            force_collection: Ignorer throttling collecte
            force_analysis: Ignorer throttling analyse
            force_stats: Ignorer throttling statistiques
            **collect_kwargs: Paramètres pour la collecte
            
        Returns:
            Résultats complets du pipeline
        """
        start_time = datetime.now()
        logger.info(f"Début pipeline {self.pipeline_name} - Max: {max_jobs}")
        
        try:
            # Initialiser la base de données
            if not await self.init_database():
                raise Exception("Impossible d'initialiser la base de données")
            
            # Variables de résultats
            collection_results = {}
            analysis_results = {}
            stats_results = {}
            
            # 1. COLLECTE (avec throttling)
            collection_check = await self.check_should_collect()
            should_collect = collection_check["should_execute"] or force_collection
            
            if should_collect:
                logger.info(f"Début collecte {self.data_collector.source_name}")
                
                # Vérifier que la méthode optimisée existe
                if not hasattr(self.data_collector, 'collect_and_save_jobs_optimized'):
                    raise RuntimeError(
                        f"Le collecteur {self.data_collector.source_name} doit implémenter "
                        "collect_and_save_jobs_optimized() pour le filtrage intelligent"
                    )
                
                collection_results = await self.data_collector.collect_and_save_jobs_optimized(
                    max_jobs, **collect_kwargs
                )
            else:
                logger.info(f"⏭️ Collecte ignorée: {collection_check['reason']}")
                collection_results = {
                    "success": True,
                    "skipped": True,
                    "reason": collection_check["reason"],
                    "source": self.data_collector.source_name,
                }
            
            # 2. ANALYSE (avec throttling)
            analysis_check = await self.check_should_analyze()
            should_analyze = analysis_check["should_execute"] or force_analysis
            
            if should_analyze:
                logger.info(f"🧠 Début analyse des compétences {self.data_collector.source_name}")
                
                # Créer le processeur de compétences
                from .competence_processor import CompetenceProcessor
                competence_processor = CompetenceProcessor(self.data_collector.source_name)
                competence_processor.set_database(self.db)
                
                # Lancer l'analyse
                analysis_results = await competence_processor.analyze_jobs_competences(
                    pipeline_name=self.pipeline_name,
                    limit_jobs=None,  # Pas de limite
                    analyze_all=True,  # Analyser tous les jobs
                    force_reanalyze=force_analysis
                )
            else:
                logger.info(f"⏭️ Analyse ignorée: {analysis_check['reason']}")
                analysis_results = {
                    "success": True, 
                    "skipped": True,
                    "reason": analysis_check["reason"]
                }
            
            # 3. STATISTIQUES (avec throttling) 
            stats_check = await self.check_should_generate_stats()
            should_generate_stats = stats_check["should_execute"] or force_stats
            
            if should_generate_stats and self.stats_generator:
                logger.info(f"Début génération statistiques {self.stats_generator.source_name}")
                stats_results = await self.stats_generator.generate_complete_statistics(
                    pipeline_name=self.pipeline_name,
                    include_temporal=True,
                    include_categories=True
                )
            elif should_generate_stats:
                logger.warning(f"⚠️ StatsGenerator non configuré pour {self.pipeline_name}")
                stats_results = {
                    "success": False,
                    "error": "StatsGenerator non configuré",
                    "source": self.data_collector.source_name
                }
            else:
                logger.info(f"⏭️ Statistiques ignorées: {stats_check['reason']}")
                stats_results = {
                    "success": True,
                    "skipped": True, 
                    "reason": stats_check["reason"]
                }
            
            # Résultats finaux
            duration = datetime.now() - start_time
            results = {
                "success": True,
                "pipeline_name": self.pipeline_name,
                "source": self.data_collector.source_name,
                "duration": str(duration),
                "timestamp": datetime.now().isoformat(),
                
                # Résultats par étape
                "collection": collection_results,
                "analysis": analysis_results,
                "statistics": stats_results,
                
                # Flags d'exécution
                "collection_executed": should_collect,
                "analysis_executed": should_analyze,
                "stats_executed": should_generate_stats,
            }
            
            logger.info(f"[OK] Pipeline {self.pipeline_name} terminé en {duration}")
            return results
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur pipeline {self.pipeline_name}: {e}")
            return {
                "success": False,
                "pipeline_name": self.pipeline_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        
        finally:
            # Nettoyage des connexions
            await self.close_database()