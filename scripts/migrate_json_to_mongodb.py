#!/usr/bin/env python3
"""
Script de migration des données JSON vers MongoDB
Migre toutes les données existantes (offres + compétences) vers MongoDB
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ajouter le backend au path Python
sys.path.append(str(Path(__file__).parent.parent))

from backend.config import Config
from backend.database import close_database, get_database, init_database
from backend.database.repositories import (
    CompetencesRepository,
    OffresRepository,
    StatsRepository,
)
from backend.models.mongodb.schemas import OffreEmploiModel
from backend.tools.logging_config import get_logger

logger = get_logger(__name__)


class MigrateurDonneesJSON:
    """Migrateur des données JSON existantes vers MongoDB"""

    def __init__(self):
        """Initialise le migrateur"""
        self.config = Config()
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"

        # Repositories MongoDB
        self.db = None
        self.offres_repo = None
        self.competences_repo = None
        self.stats_repo = None

    async def init_mongodb(self) -> bool:
        """Initialise la connexion MongoDB"""
        try:
            success = await init_database()
            if not success:
                logger.error("Échec initialisation MongoDB")
                return False

            self.db = get_database()
            self.offres_repo = OffresRepository(self.db)
            self.competences_repo = CompetencesRepository(self.db)
            self.stats_repo = StatsRepository(self.db)

            logger.info("✅ Connexion MongoDB établie")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            return False

    async def close_mongodb(self):
        """Ferme la connexion MongoDB"""
        try:
            await close_database()
            logger.info("Connexion MongoDB fermée")
        except Exception as e:
            logger.warning(f"Erreur fermeture: {e}")

    def lister_fichiers_offres(self) -> list[Path]:
        """Liste tous les fichiers d'offres JSON"""
        pattern = "offres_M1805_FRANCE_*.json"
        fichiers = list(self.data_dir.glob(pattern))
        fichiers.sort(reverse=True)  # Plus récents en premier

        logger.info(f"📁 {len(fichiers)} fichiers d'offres trouvés")
        return fichiers

    def lister_fichiers_competences(self) -> list[Path]:
        """Liste tous les fichiers de compétences JSON"""
        pattern = "competences_extraites_*.json"
        fichiers = list(self.data_dir.glob(pattern))
        fichiers.sort(reverse=True)

        logger.info(f"🧠 {len(fichiers)} fichiers de compétences trouvés")
        return fichiers

    def charger_offres_depuis_json(self, fichier: Path) -> list[dict]:
        """Charge les offres depuis un fichier JSON"""
        try:
            with open(fichier, encoding='utf-8') as f:
                data = json.load(f)

            # Gérer les différents formats de fichiers
            if isinstance(data, list):
                offres = data
            elif isinstance(data, dict) and 'offres' in data:
                offres = data['offres']
            elif isinstance(data, dict) and 'resultats' in data:
                offres = data['resultats']
            else:
                logger.warning(f"Format de fichier non reconnu: {fichier.name}")
                return []

            logger.info(f"📊 {len(offres)} offres chargées depuis {fichier.name}")
            return offres

        except Exception as e:
            logger.error(f"❌ Erreur chargement {fichier.name}: {e}")
            return []

    def convertir_offre_json_vers_modele(self, offre_json: dict, fichier_source: str) -> OffreEmploiModel:
        """
        Convertit une offre JSON en modèle MongoDB
        
        Args:
            offre_json: Offre au format JSON
            fichier_source: Nom du fichier source
            
        Returns:
            Modèle OffreEmploiModel
        """
        # Extraction des informations selon le format JSON
        source_id = str(offre_json.get("id", ""))

        # Dates avec gestion des différents formats
        date_creation = self._parse_date_json(
            offre_json.get("dateCreation") or offre_json.get("date_creation")
        )
        date_maj = self._parse_date_json(
            offre_json.get("dateActualisation") or offre_json.get("date_actualisation")
        )

        # Entreprise
        entreprise_info = offre_json.get("entreprise", {})
        if isinstance(entreprise_info, dict):
            entreprise = {
                "nom": entreprise_info.get("nom", ""),
                "description": entreprise_info.get("description", ""),
            }
        else:
            entreprise = {"nom": str(entreprise_info) if entreprise_info else ""}

        # Localisation
        lieu_travail = offre_json.get("lieuTravail", {})
        localisation = {
            "ville": lieu_travail.get("libelle", "") if lieu_travail else "",
            "code_postal": lieu_travail.get("codePostal", "") if lieu_travail else "",
            "departement": "",
            "region": "",
        }

        # Calculer le département depuis le code postal
        if localisation["code_postal"]:
            localisation["departement"] = localisation["code_postal"][:2]

        # Contrat
        contrat = {
            "type": offre_json.get("typeContrat", ""),
            "libelle": offre_json.get("typeContratLibelle", ""),
            "duree": offre_json.get("dureeTravail", ""),
        }

        # Extraction du timestamp depuis le nom de fichier
        timestamp_collecte = self._extraire_timestamp_fichier(fichier_source)

        return OffreEmploiModel(
            source_id=source_id,
            intitule=offre_json.get("intitule", ""),
            description=offre_json.get("description", ""),
            date_creation=date_creation or datetime.now(),
            date_mise_a_jour=date_maj,
            date_collecte=timestamp_collecte,
            entreprise=entreprise,
            localisation=localisation,
            contrat=contrat,
            competences_extraites=[],  # Sera enrichi plus tard
            code_rome="M1805",
            source="migration_json",
            traite=False,
        )

    def _parse_date_json(self, date_str: str | None) -> datetime | None:
        """Parse une date depuis le JSON avec gestion des formats multiples"""
        if not date_str:
            return None

        try:
            # Format ISO avec timezone
            if "T" in date_str and ("Z" in date_str or "+" in date_str):
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            # Format ISO simple
            elif "T" in date_str:
                return datetime.fromisoformat(date_str)
            # Format date simple
            elif "-" in date_str:
                return datetime.fromisoformat(date_str)
            else:
                return None
        except Exception:
            logger.warning(f"Format de date non reconnu: {date_str}")
            return None

    def _extraire_timestamp_fichier(self, nom_fichier: str) -> datetime:
        """Extrait le timestamp depuis le nom de fichier"""
        try:
            # Format: offres_M1805_FRANCE_20251015_064147.json
            parties = nom_fichier.split("_")
            if len(parties) >= 4:
                date_str = parties[3]  # 20251015
                heure_str = parties[4].split(".")[0]  # 064147

                timestamp_str = f"{date_str}_{heure_str}"
                return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except Exception:
            pass

        return datetime.now()

    async def migrer_offres(self, limite_fichiers: int | None = None) -> dict[str, Any]:
        """
        Migre les offres JSON vers MongoDB
        
        Args:
            limite_fichiers: Nombre max de fichiers à traiter
            
        Returns:
            Statistiques de migration
        """
        logger.info("🚀 Début migration des offres")

        fichiers_offres = self.lister_fichiers_offres()
        if limite_fichiers:
            fichiers_offres = fichiers_offres[:limite_fichiers]

        stats = {
            "fichiers_traites": 0,
            "offres_lues": 0,
            "offres_converties": 0,
            "offres_sauvegardees": 0,
            "erreurs": 0,
        }

        for fichier in fichiers_offres:
            logger.info(f"📁 Traitement: {fichier.name}")

            try:
                # Charger les offres JSON
                offres_json = self.charger_offres_depuis_json(fichier)
                stats["offres_lues"] += len(offres_json)

                # Convertir en modèles MongoDB
                offres_modeles = []
                for offre_json in offres_json:
                    try:
                        modele = self.convertir_offre_json_vers_modele(offre_json, fichier.name)
                        offres_modeles.append(modele)
                        stats["offres_converties"] += 1
                    except Exception as e:
                        stats["erreurs"] += 1
                        logger.warning(f"Erreur conversion offre {offre_json.get('id')}: {e}")

                # Sauvegarder en lot dans MongoDB
                if offres_modeles:
                    nb_sauvegardees = await self.offres_repo.insert_many_offres(offres_modeles)
                    stats["offres_sauvegardees"] += nb_sauvegardees
                    logger.info(f"✅ {nb_sauvegardees} offres sauvegardées")

                stats["fichiers_traites"] += 1

            except Exception as e:
                stats["erreurs"] += 1
                logger.error(f"❌ Erreur traitement {fichier.name}: {e}")

        logger.info("🎉 Migration des offres terminée")
        return stats

    def charger_competences_depuis_json(self, fichier: Path) -> dict[str, Any]:
        """Charge les compétences depuis un fichier JSON"""
        try:
            with open(fichier, encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"🧠 Compétences chargées depuis {fichier.name}")
            return data

        except Exception as e:
            logger.error(f"❌ Erreur chargement compétences {fichier.name}: {e}")
            return {}

    async def migrer_competences(self) -> dict[str, Any]:
        """Migre les compétences analysées vers MongoDB"""
        logger.info("🧠 Début migration des compétences")

        fichiers_competences = self.lister_fichiers_competences()

        stats = {
            "fichiers_traites": 0,
            "competences_uniques": set(),
            "detections_sauvegardees": 0,
            "offres_mises_a_jour": 0,
        }

        for fichier in fichiers_competences:
            logger.info(f"📁 Traitement compétences: {fichier.name}")

            try:
                data = self.charger_competences_depuis_json(fichier)

                # Traiter selon le format du fichier de compétences
                if "competences_par_offre" in data:
                    await self._migrer_competences_par_offre(data["competences_par_offre"], stats)

                if "top_competences" in data:
                    await self._migrer_top_competences(data["top_competences"], stats)

                stats["fichiers_traites"] += 1

            except Exception as e:
                logger.error(f"❌ Erreur migration compétences {fichier.name}: {e}")

        # Créer ou mettre à jour les compétences uniques
        await self._creer_competences_uniques(stats["competences_uniques"])

        logger.info("🎉 Migration des compétences terminée")
        return dict(stats)

    async def _migrer_competences_par_offre(self, competences_par_offre: dict, stats: dict):
        """Migre les compétences détectées par offre"""
        detections = []

        for offre_id, competences in competences_par_offre.items():
            competences_noms = []

            for competence in competences:
                nom_competence = competence.get("nom", "") if isinstance(competence, dict) else str(competence)
                competences_noms.append(nom_competence)
                stats["competences_uniques"].add(nom_competence)

                # Créer une détection
                detection = {
                    "offre_id": str(offre_id),
                    "competence": nom_competence,
                    "methode_detection": "migration_json",
                    "confiance": competence.get("score", 1.0) if isinstance(competence, dict) else 1.0,
                    "contexte": competence.get("contexte", "") if isinstance(competence, dict) else "",
                    "date_detection": datetime.now(),
                }
                detections.append(detection)

            # Mettre à jour l'offre avec les compétences
            try:
                await self.offres_repo.collection.update_one(
                    {"source_id": str(offre_id)},
                    {
                        "$set": {
                            "competences_extraites": competences_noms,
                            "traite": True,
                            "date_traitement": datetime.now(),
                        }
                    }
                )
                stats["offres_mises_a_jour"] += 1
            except Exception as e:
                logger.warning(f"Erreur MAJ offre {offre_id}: {e}")

        # Insérer les détections en lot
        if detections:
            try:
                await self.db.competences_detections.insert_many(detections)
                stats["detections_sauvegardees"] += len(detections)
            except Exception as e:
                logger.error(f"Erreur sauvegarde détections: {e}")

    async def _migrer_top_competences(self, top_competences: list, stats: dict):
        """Migre les statistiques de compétences"""
        for item in top_competences:
            if isinstance(item, dict) and "competence" in item:
                stats["competences_uniques"].add(item["competence"])

    async def _creer_competences_uniques(self, competences_noms: set):
        """Crée les compétences uniques dans la collection"""
        competences_a_creer = []

        for nom in competences_noms:
            if nom and len(nom.strip()) > 1:
                competence = {
                    "nom": nom,
                    "nom_normalise": nom.lower().strip(),
                    "categorie": "technique",  # Par défaut
                    "synonymes": [],
                    "description": f"Compétence migré: {nom}",
                    "niveau_demande": "confirme",
                    "frequence_detection": 1,
                    "derniere_detection": datetime.now(),
                }
                competences_a_creer.append(competence)

        if competences_a_creer:
            try:
                # Insérer avec upsert pour éviter les doublons
                for competence in competences_a_creer:
                    await self.db.competences.update_one(
                        {"nom_normalise": competence["nom_normalise"]},
                        {"$set": competence},
                        upsert=True
                    )

                logger.info(f"✅ {len(competences_a_creer)} compétences uniques créées/mises à jour")

            except Exception as e:
                logger.error(f"❌ Erreur création compétences: {e}")

    async def generer_statistiques_migration(self) -> dict[str, Any]:
        """Génère les statistiques post-migration"""
        logger.info("📊 Génération des statistiques de migration")

        try:
            # Statistiques des offres
            stats_offres = await self.offres_repo.get_collection_stats()

            # Statistiques des compétences
            nb_competences = await self.db.competences.count_documents({})
            nb_detections = await self.db.competences_detections.count_documents({})

            # Top compétences
            pipeline = [
                {"$unwind": "$competences_extraites"},
                {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            cursor = self.offres_repo.collection.aggregate(pipeline)
            top_competences = await cursor.to_list(length=10)

            statistiques = {
                "date_migration": datetime.now(),
                "offres": {
                    "total": stats_offres.get("total_offres", 0),
                    "traitees": await self.offres_repo.collection.count_documents({"traite": True}),
                },
                "competences": {
                    "uniques": nb_competences,
                    "detections_total": nb_detections,
                },
                "top_competences_migrees": [
                    {"competence": item["_id"], "occurrences": item["count"]}
                    for item in top_competences
                ],
            }

            # Sauvegarder les statistiques
            await self.db.stats_competences.insert_one({
                "periode_analysee": f"migration_{datetime.now().strftime('%Y%m%d')}",
                "date_analyse": datetime.now(),
                "nb_offres_analysees": statistiques["offres"]["total"],
                "source": "migration_json",
                "details": statistiques,
            })

            return statistiques

        except Exception as e:
            logger.error(f"❌ Erreur génération statistiques: {e}")
            return {}

    async def executer_migration_complete(
        self, limite_fichiers_offres: int | None = None
    ) -> dict[str, Any]:
        """
        Exécute la migration complète JSON → MongoDB
        
        Args:
            limite_fichiers_offres: Limite de fichiers d'offres à traiter
            
        Returns:
            Résultats complets de la migration
        """
        start_time = datetime.now()
        logger.info("🚀 DÉBUT MIGRATION COMPLÈTE JSON → MONGODB")

        try:
            # 1. Initialiser MongoDB
            if not await self.init_mongodb():
                raise Exception("Échec initialisation MongoDB")

            # 2. Migrer les offres
            stats_offres = await self.migrer_offres(limite_fichiers_offres)

            # 3. Migrer les compétences
            stats_competences = await self.migrer_competences()

            # 4. Générer les statistiques finales
            stats_finales = await self.generer_statistiques_migration()

            duree = datetime.now() - start_time

            resultats = {
                "success": True,
                "duree_migration": str(duree),
                "migration_offres": stats_offres,
                "migration_competences": stats_competences,
                "statistiques_finales": stats_finales,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"🎉 MIGRATION TERMINÉE AVEC SUCCÈS - Durée: {duree}")
            return resultats

        except Exception as e:
            logger.error(f"❌ ÉCHEC MIGRATION: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        finally:
            await self.close_mongodb()


def afficher_resultats_migration(resultats: dict[str, Any]):
    """Affiche les résultats de migration de façon lisible"""
    print("\n" + "="*70)
    print("📊 RÉSULTATS DE MIGRATION JSON → MONGODB")
    print("="*70)

    if resultats.get("success"):
        print(f"✅ Succès - Durée: {resultats.get('duree_migration')}")

        # Statistiques offres
        stats_offres = resultats.get("migration_offres", {})
        print("\n📄 OFFRES:")
        print(f"   Fichiers traités: {stats_offres.get('fichiers_traites', 0)}")
        print(f"   Offres lues: {stats_offres.get('offres_lues', 0):,}")
        print(f"   Offres converties: {stats_offres.get('offres_converties', 0):,}")
        print(f"   Offres sauvegardées: {stats_offres.get('offres_sauvegardees', 0):,}")
        print(f"   Erreurs: {stats_offres.get('erreurs', 0)}")

        # Statistiques compétences
        stats_comp = resultats.get("migration_competences", {})
        print("\n🧠 COMPÉTENCES:")
        print(f"   Fichiers traités: {stats_comp.get('fichiers_traites', 0)}")
        print(f"   Compétences uniques: {len(stats_comp.get('competences_uniques', []))}")
        print(f"   Détections sauvegardées: {stats_comp.get('detections_sauvegardees', 0):,}")
        print(f"   Offres mises à jour: {stats_comp.get('offres_mises_a_jour', 0):,}")

        # Statistiques finales
        stats_finales = resultats.get("statistiques_finales", {})
        if stats_finales:
            offres_info = stats_finales.get("offres", {})
            print("\n📊 BILAN FINAL:")
            print(f"   Total offres en base: {offres_info.get('total', 0):,}")
            print(f"   Offres traitées: {offres_info.get('traitees', 0):,}")

            comp_info = stats_finales.get("competences", {})
            print(f"   Compétences uniques: {comp_info.get('uniques', 0):,}")
            print(f"   Total détections: {comp_info.get('detections_total', 0):,}")

        print("\n🎯 MongoDB est prêt avec toutes vos données historiques!")

    else:
        print(f"❌ Échec: {resultats.get('error')}")


async def main():
    """Fonction principale"""
    print("🚀 Migration des données JSON vers MongoDB - DatavizFT")
    print("=" * 60)

    import argparse
    parser = argparse.ArgumentParser(description="Migration JSON vers MongoDB")
    parser.add_argument("--limite", type=int, help="Limite de fichiers d'offres à traiter")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans sauvegarde")

    args = parser.parse_args()

    if args.dry_run:
        print("⚠️ MODE SIMULATION - Aucune donnée ne sera sauvegardée")
        return

    migrateur = MigrateurDonneesJSON()
    resultats = await migrateur.executer_migration_complete(args.limite)

    afficher_resultats_migration(resultats)

    return resultats.get("success", False)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
