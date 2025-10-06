"""
File Manager - Gestion des fichiers et sauvegarde
Sauvegarde des offres, résultats d'analyse et gestion des dossiers
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .text_processor import nettoyer_offres_pour_json


class FileManager:
    """Gestionnaire de fichiers pour les données du projet"""

    def __init__(self, base_path: Path | None = None):
        """
        Initialise le gestionnaire avec le chemin de base

        Args:
            base_path: Chemin de base du projet (par défaut: racine du projet)
        """
        if base_path is None:
            # Chemin vers la racine du projet depuis backend/tools/
            self.base_path = Path(__file__).parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.data_dir = self.base_path / "data"
        self.results_dir = self.data_dir / "json_results"

    def creer_structure_dossiers(self):
        """Crée la structure de dossiers nécessaire"""
        self.data_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        print(f"✅ Structure de dossiers créée: {self.data_dir}")

    def sauvegarder_offres(
        self, offres: list[dict[str, Any]], code_rome: str = "M1805"
    ) -> str:
        """
        Sauvegarde les offres collectées en JSON

        Args:
            offres: Liste des offres à sauvegarder
            code_rome: Code ROME pour le nommage du fichier

        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"offres_{code_rome}_FRANCE_{timestamp}.json"
        chemin_fichier = self.data_dir / nom_fichier

        # Nettoyage des offres pour éliminer les caractères Unicode problématiques
        print("🧹 Nettoyage des caractères Unicode...")
        offres_nettoyees = nettoyer_offres_pour_json(offres)

        # Préparation des métadonnées
        donnees_complete = {
            "metadata": {
                "date_collecte": datetime.now().isoformat(),
                "nb_offres": len(offres_nettoyees),
                "code_rome": code_rome,
                "source": "France Travail API v2",
                "version_collector": "DatavizFT v1.0",
            },
            "offres": offres_nettoyees,
        }

        try:
            with open(chemin_fichier, "w", encoding="utf-8", newline="\n") as f:
                json.dump(
                    donnees_complete,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=False,
                    separators=(",", ": "),
                )

            print(f"💾 Offres sauvegardées: {chemin_fichier}")
            print(
                f"📊 {len(offres_nettoyees)} offres - {chemin_fichier.stat().st_size // 1024} Ko"
            )
            print("🧹 Caractères Unicode normalisés")

            return str(chemin_fichier)

        except Exception as e:
            print(f"❌ Erreur sauvegarde offres: {e}")
            raise

    def sauvegarder_analyse_competences(
        self, resultats: dict[str, Any], code_rome: str = "M1805"
    ) -> str:
        """
        Sauvegarde l'analyse de compétences en JSON

        Args:
            resultats: Résultats de l'analyse des compétences
            code_rome: Code ROME pour le nommage du fichier

        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"analyse_competences_{code_rome}_{timestamp}.json"
        chemin_fichier = self.results_dir / nom_fichier

        # Préparation des métadonnées
        donnees_complete = {
            "metadata": {
                "date_analyse": datetime.now().isoformat(),
                "code_rome": code_rome,
                "nb_offres_analysees": resultats.get("nb_offres_analysees", 0),
                "version_analyzer": "DatavizFT v1.0",
            },
            "analyse": resultats,
        }

        try:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(donnees_complete, f, ensure_ascii=False, indent=2)

            print(f"📊 Analyse sauvegardée: {chemin_fichier}")
            return str(chemin_fichier)

        except Exception as e:
            print(f"❌ Erreur sauvegarde analyse: {e}")
            raise

    def sauvegarder_competences_enrichies(
        self,
        resultats_par_categorie: dict[str, Any],
        nb_offres_total: int,
        code_rome: str = "M1805",
    ) -> str:
        """
        Sauvegarde les compétences enrichies avec métadonnées complètes

        Args:
            resultats_par_categorie: Résultats par catégorie
            nb_offres_total: Nombre total d'offres analysées
            code_rome: Code ROME

        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"competences_extraites_{timestamp}.json"
        chemin_fichier = self.data_dir / nom_fichier

        # Calcul des statistiques globales
        total_competences_detectees = sum(
            len(cat["competences"]) for cat in resultats_par_categorie.values()
        )

        # Création du top global
        top_competences = []
        for categorie, resultats in resultats_par_categorie.items():
            for comp in resultats["competences"]:
                top_competences.append({**comp, "categorie": categorie})

        top_competences.sort(key=lambda x: x["occurrences"], reverse=True)

        # Structure enrichie
        competences_enrichies = {
            "metadata": {
                "date_extraction": datetime.now().isoformat(),
                "code_rome": code_rome,
                "nb_offres_analysees": nb_offres_total,
                "nb_competences_detectees": total_competences_detectees,
                "nb_categories": len(resultats_par_categorie),
                "version": "DatavizFT v1.0",
            },
            "resume_global": {
                "top_10_competences": top_competences[:10],
                "repartition_par_categorie": {
                    cat: len(res["competences"])
                    for cat, res in resultats_par_categorie.items()
                },
            },
            "resultats_detailles": resultats_par_categorie,
        }

        try:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(competences_enrichies, f, ensure_ascii=False, indent=2)

            print(f"🎯 Compétences enrichies sauvegardées: {chemin_fichier}")
            print(f"📈 {total_competences_detectees} compétences détectées")

            return str(chemin_fichier)

        except Exception as e:
            print(f"❌ Erreur sauvegarde compétences enrichies: {e}")
            raise

    def charger_offres(self, chemin_fichier: str) -> list[dict[str, Any]]:
        """
        Charge les offres depuis un fichier JSON

        Args:
            chemin_fichier: Chemin vers le fichier d'offres

        Returns:
            Liste des offres chargées
        """
        try:
            with open(chemin_fichier, encoding="utf-8") as f:
                data = json.load(f)

            # Support des deux formats (avec/sans métadonnées)
            if isinstance(data, list):
                return data
            elif "offres" in data:
                return data["offres"]
            else:
                raise ValueError("Format de fichier non reconnu")

        except Exception as e:
            print(f"❌ Erreur chargement offres: {e}")
            raise

    def lister_fichiers_offres(self, pattern: str = "offres_*.json") -> list[str]:
        """
        Liste les fichiers d'offres disponibles

        Args:
            pattern: Pattern de recherche des fichiers

        Returns:
            Liste des chemins de fichiers trouvés
        """
        fichiers = list(self.data_dir.glob(pattern))
        return [
            str(f) for f in sorted(fichiers, reverse=True)
        ]  # Plus récents en premier

    def lister_fichiers_analyses(self, pattern: str = "analyse_*.json") -> list[str]:
        """
        Liste les fichiers d'analyses disponibles

        Args:
            pattern: Pattern de recherche des fichiers

        Returns:
            Liste des chemins de fichiers trouvés
        """
        fichiers = list(self.results_dir.glob(pattern))
        return [str(f) for f in sorted(fichiers, reverse=True)]

    def nettoyer_anciens_fichiers(self, nb_a_garder: int = 5):
        """
        Nettoie les anciens fichiers en gardant les N plus récents

        Args:
            nb_a_garder: Nombre de fichiers récents à conserver
        """
        patterns = ["offres_*.json", "analyse_*.json", "competences_extraites_*.json"]

        for pattern in patterns:
            fichiers = list(self.data_dir.glob(pattern)) + list(
                self.results_dir.glob(pattern)
            )
            fichiers_tries = sorted(
                fichiers, key=lambda x: x.stat().st_mtime, reverse=True
            )

            # Supprimer les fichiers en surplus
            for fichier in fichiers_tries[nb_a_garder:]:
                try:
                    fichier.unlink()
                    print(f"🗑️ Supprimé: {fichier.name}")
                except Exception as e:
                    print(f"❌ Erreur suppression {fichier.name}: {e}")

    def obtenir_statistiques_stockage(self) -> dict[str, Any]:
        """
        Obtient les statistiques de stockage

        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            "dossiers": {"data": str(self.data_dir), "results": str(self.results_dir)},
            "fichiers": {
                "offres": len(list(self.data_dir.glob("offres_*.json"))),
                "analyses": len(list(self.results_dir.glob("analyse_*.json"))),
                "competences": len(
                    list(self.data_dir.glob("competences_extraites_*.json"))
                ),
            },
        }

        # Calcul de la taille totale
        taille_totale = 0
        for fichier in self.data_dir.rglob("*.json"):
            taille_totale += fichier.stat().st_size

        stats["taille_totale_mb"] = round(taille_totale / (1024 * 1024), 2)

        return stats


# Fonctions utilitaires pour compatibilité
def sauvegarder_offres_simple(
    offres: list[dict[str, Any]], code_rome: str = "M1805"
) -> str:
    """Fonction de compatibilité pour sauvegarder des offres"""
    manager = FileManager()
    manager.creer_structure_dossiers()
    return manager.sauvegarder_offres(offres, code_rome)


def sauvegarder_competences_simple(
    resultats_par_categorie: dict[str, Any],
    nb_offres_total: int,
    code_rome: str = "M1805",
) -> str:
    """Fonction de compatibilité pour sauvegarder les compétences"""
    manager = FileManager()
    return manager.sauvegarder_competences_enrichies(
        resultats_par_categorie, nb_offres_total, code_rome
    )
