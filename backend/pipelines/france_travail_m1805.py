"""
Pipeline France Travail M1805 - Version refactorisée
Collecte et analyse des offres d'emploi pour le code ROME M1805 (Études et développement informatique)
"""

import os
import glob
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..tools.data_loader import charger_competences_referentiel, charger_config_pipeline
from ..tools.api_client import FranceTravailAPIClient
from ..tools.competence_analyzer import CompetenceAnalyzer
from ..tools.file_manager import FileManager


class PipelineM1805:
    """Pipeline de collecte et d'analyse pour les offres M1805"""
    
    def __init__(self):
        """Initialise le pipeline avec ses composants"""
        self.config = charger_config_pipeline("france_travail_m1805")
        self.competences_referentiel = charger_competences_referentiel()
        
        # Initialisation des composants
        self.api_client = FranceTravailAPIClient(
            user_agent=self.config.get("user_agent", "DatavizFT-Collector/1.0"),
            rate_limit_ms=self.config.get("rate_limit_ms", 120)
        )
        
        self.analyzer = CompetenceAnalyzer(self.competences_referentiel)
        self.file_manager = FileManager()
        
        # Configuration
        self.code_rome = self.config.get("code_rome", "M1805")
        
        print(f"🚀 Pipeline M1805 initialisé")
        print(f"📋 {len(self.competences_referentiel)} catégories de compétences chargées")
    
    def verifier_derniere_execution(self) -> Dict[str, Any]:
        """
        Vérifie si le pipeline a été exécuté dans les 24 dernières heures
        
        Returns:
            Dict contenant le statut et les informations de la dernière exécution
        """
        try:
            # Rechercher les fichiers d'offres M1805 dans le dossier data
            pattern = "data/offres_M1805_FRANCE_*.json"
            fichiers_offres = glob.glob(pattern)
            
            if not fichiers_offres:
                return {
                    "doit_executer": True,
                    "raison": "Aucun fichier d'offres trouvé",
                    "dernier_fichier": None,
                    "derniere_execution": None
                }
            
            # Trier par nom (le timestamp est dans le nom) pour avoir le plus récent
            fichiers_offres.sort(reverse=True)
            dernier_fichier = fichiers_offres[0]
            
            # Extraire le timestamp du nom de fichier (format: YYYYMMDD_HHMMSS)
            nom_fichier = os.path.basename(dernier_fichier)
            # Format: offres_M1805_FRANCE_20251005_091707.json
            parties = nom_fichier.split('_')
            if len(parties) >= 4:
                date_str = parties[3]  # 20251005
                heure_str = parties[4].split('.')[0]  # 091707
                
                # Convertir en datetime
                timestamp_str = f"{date_str}_{heure_str}"
                derniere_execution = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                # Vérifier si c'est dans les 24 dernières heures
                maintenant = datetime.now()
                difference = maintenant - derniere_execution
                
                if difference < timedelta(hours=24):
                    return {
                        "doit_executer": False,
                        "raison": f"Exécution récente il y a {difference}",
                        "dernier_fichier": dernier_fichier,
                        "derniere_execution": derniere_execution,
                        "heures_restantes": 24 - difference.total_seconds() / 3600
                    }
                else:
                    return {
                        "doit_executer": True,
                        "raison": f"Dernière exécution il y a {difference} (> 24h)",
                        "dernier_fichier": dernier_fichier,
                        "derniere_execution": derniere_execution
                    }
            else:
                return {
                    "doit_executer": True,
                    "raison": "Format de fichier non reconnu",
                    "dernier_fichier": dernier_fichier,
                    "derniere_execution": None
                }
                
        except Exception as e:
            return {
                "doit_executer": True,
                "raison": f"Erreur lors de la vérification: {e}",
                "dernier_fichier": None,
                "derniere_execution": None
            }
    
    def collecter_offres(self, max_offres: Optional[int] = None) -> list:
        """
        Collecte les offres d'emploi M1805
        
        Args:
            max_offres: Limite optionnelle du nombre d'offres
        
        Returns:
            Liste des offres collectées
        """
        print(f"\n🔍 COLLECTE DES OFFRES {self.code_rome}")
        print("=" * 50)
        
        offres = self.api_client.collecter_offres_par_code_rome(
            self.code_rome,
            max_offres=max_offres
        )
        
        print(f"✅ {len(offres)} offres collectées")
        return offres
    
    def analyser_competences(self, offres: list) -> Dict[str, Any]:
        """
        Analyse les compétences dans les offres
        
        Args:
            offres: Liste des offres à analyser
        
        Returns:
            Résultats de l'analyse
        """
        print(f"\n🎯 ANALYSE DES COMPÉTENCES")
        print("=" * 50)
        
        resultats = self.analyzer.analyser_offres(offres, verbose=True)
        
        print(f"✅ Analyse terminée")
        return resultats
    
    def sauvegarder_donnees(self, offres: list, resultats_analyse: Dict[str, Any]) -> Dict[str, str]:
        """
        Sauvegarde les offres et les résultats d'analyse
        
        Args:
            offres: Liste des offres
            resultats_analyse: Résultats de l'analyse
        
        Returns:
            Dict avec les chemins des fichiers sauvegardés
        """
        print(f"\n💾 SAUVEGARDE DES DONNÉES")
        print("=" * 50)
        
        # Créer la structure de dossiers
        self.file_manager.creer_structure_dossiers()
        
        # Sauvegarder les offres
        chemin_offres = self.file_manager.sauvegarder_offres(offres, self.code_rome)
        
        # Sauvegarder l'analyse complète
        chemin_analyse = self.file_manager.sauvegarder_analyse_competences(
            resultats_analyse, self.code_rome
        )
        
        # Sauvegarder les compétences enrichies
        chemin_competences = self.file_manager.sauvegarder_competences_enrichies(
            resultats_analyse['resultats_par_categorie'],
            resultats_analyse['nb_offres_analysees'],
            self.code_rome
        )
        
        chemins = {
            "offres": chemin_offres,
            "analyse": chemin_analyse, 
            "competences": chemin_competences
        }
        
        print(f"✅ Toutes les données sauvegardées")
        return chemins
    
    def executer_pipeline_complet(self, max_offres: Optional[int] = None) -> Dict[str, Any]:
        """
        Exécute le pipeline complet de collecte et d'analyse
        
        Args:
            max_offres: Limite optionnelle du nombre d'offres
        
        Returns:
            Dict avec les résultats et informations du pipeline
        """
        print(f"🚀 EXÉCUTION DU PIPELINE COMPLET M1805")
        print("=" * 70)
        
        try:
            # 1. Collecte des offres
            offres = self.collecter_offres(max_offres)
            
            if not offres:
                return {
                    "success": False,
                    "error": "Aucune offre collectée",
                    "nb_offres": 0
                }
            
            # 2. Analyse des compétences
            resultats_analyse = self.analyser_competences(offres)
            
            # 3. Sauvegarde
            chemins_fichiers = self.sauvegarder_donnees(offres, resultats_analyse)
            
            # 4. Résumé final
            print(f"\n🎉 PIPELINE TERMINÉ AVEC SUCCÈS")
            print("=" * 70)
            print(f"📊 {len(offres)} offres M1805 collectées et analysées")
            print(f"📁 Fichiers générés dans le dossier data/")
            
            return {
                "success": True,
                "nb_offres": len(offres),
                "nb_competences_detectees": sum(
                    len(cat['competences']) 
                    for cat in resultats_analyse['resultats_par_categorie'].values()
                ),
                "fichiers_generes": chemins_fichiers,
                "resultats_analyse": resultats_analyse
            }
            
        except Exception as e:
            print(f"\n❌ ERREUR PIPELINE: {e}")
            return {
                "success": False,
                "error": str(e),
                "nb_offres": 0
            }
    
    def obtenir_statistiques_pipeline(self) -> Dict[str, Any]:
        """
        Obtient les statistiques du pipeline et des données
        
        Returns:
            Dict avec les statistiques complètes
        """
        stats_stockage = self.file_manager.obtenir_statistiques_stockage()
        
        return {
            "config": self.config,
            "code_rome": self.code_rome,
            "nb_categories_competences": len(self.competences_referentiel),
            "nb_competences_total": sum(len(comp) for comp in self.competences_referentiel.values()),
            "stockage": stats_stockage
        }


# Fonction principale pour compatibilité avec l'ancien système
def run_pipelineFT(forcer_execution: bool = False) -> Dict[str, Any]:
    """
    Point d'entrée principal du pipeline - maintient la compatibilité
    Vérifie automatiquement si une exécution récente existe (< 24h)
    
    Args:
        forcer_execution: Si True, force l'exécution même si récente
    
    Returns:
        Résultats de l'exécution du pipeline
    """
    pipeline = PipelineM1805()
    
    # Vérifier la dernière exécution si pas de forçage
    if not forcer_execution:
        verification = pipeline.verifier_derniere_execution()
        
        if not verification["doit_executer"]:
            print(f"⏭️ EXÉCUTION IGNORÉE: {verification['raison']}")
            if verification.get('heures_restantes'):
                heures = verification['heures_restantes']
                print(f"⏰ Prochaine exécution possible dans {heures:.1f} heures")
            print(f"📁 Dernier fichier: {os.path.basename(verification['dernier_fichier'])}")
            print("💡 Utilisez forcer_execution=True pour exécuter quand même")
            
            return {
                "success": True,
                "skipped": True,
                "nb_offres": 0,
                "raison": verification["raison"],
                "derniere_execution": verification.get("derniere_execution"),
                "dernier_fichier": verification.get("dernier_fichier")
            }
        else:
            print(f"✅ EXÉCUTION AUTORISÉE: {verification['raison']}")
    else:
        print("🔥 EXÉCUTION FORCÉE (ignorant la vérification des 24h)")
    
    return pipeline.executer_pipeline_complet()


# Fonction pour exécution avec paramètres
def run_pipeline_avec_limite(max_offres: int) -> Dict[str, Any]:
    """
    Exécute le pipeline avec une limite d'offres
    
    Args:
        max_offres: Nombre maximum d'offres à collecter
    
    Returns:
        Résultats de l'exécution du pipeline
    """
    pipeline = PipelineM1805()
    return pipeline.executer_pipeline_complet(max_offres=max_offres)


if __name__ == "__main__":
    # Test direct du pipeline
    resultat = run_pipelineFT()
    if resultat["success"]:
        if resultat.get("skipped"):
            print(f"⏭️ Pipeline ignoré: {resultat.get('raison', 'Exécution récente')}")
        else:
            print(f"✅ Pipeline réussi: {resultat['nb_offres']} offres traitées")
    else:
        print(f"❌ Pipeline échoué: {resultat.get('error', 'Erreur inconnue')}")