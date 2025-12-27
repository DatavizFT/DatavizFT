"""
Tests pour StatsGenerator
=========================

Vérifie la génération de statistiques par compétences.
"""

import asyncio
import pytest
from datetime import datetime
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock


class MockJobRepository:
    """Mock du repository d'offres pour les tests"""

    def __init__(self, jobs_data: List[dict]):
        self.jobs_data = jobs_data

    async def count_documents(self, filter_query: dict) -> int:
        """Compte les documents matchant le filtre"""
        source = filter_query.get("source")
        if source:
            return len([j for j in self.jobs_data if j.get("source") == source])
        return len(self.jobs_data)

    async def aggregate(self, pipeline: List[dict]) -> List[dict]:
        """Simule l'agrégation MongoDB"""
        # Simplification: on détecte le type de pipeline par sa structure

        # Pipeline pour répartition mensuelle
        if any("$group" in stage and "_id" in stage.get("$group", {})
               and "year" in str(stage.get("$group", {}).get("_id", {}))
               for stage in pipeline):

            # Vérifie si c'est le pipeline d'évolution temporelle
            is_temporal = any(
                "$group" in stage and "day" in str(stage.get("$group", {}).get("_id", {}))
                for stage in pipeline
            )

            if is_temporal:
                return [
                    {"_id": {"year": 2024, "month": 12, "day": 15}, "nb_offres": 5},
                    {"_id": {"year": 2024, "month": 12, "day": 16}, "nb_offres": 8},
                ]

            return [
                {"_id": {"year": 2024, "month": 12}, "count": 10},
                {"_id": {"year": 2024, "month": 11}, "count": 8},
            ]

        # Pipeline pour top compétences
        if any("$unwind" in stage and "$competences_extraites" in str(stage) for stage in pipeline):
            # Vérifie si c'est un pipeline de détail par catégorie
            has_match_in = any(
                "$match" in stage and "$in" in str(stage.get("$match", {}))
                for stage in pipeline
            )

            if has_match_in:
                # Pipeline détail catégorie
                return [
                    {"_id": "Python", "count": 8},
                    {"_id": "Django", "count": 5},
                ]

            # Pipeline top compétences global
            return [
                {"_id": "Python", "count": 8},
                {"_id": "JavaScript", "count": 6},
                {"_id": "Docker", "count": 4},
            ]

        # Pipeline pour comptage par catégorie
        if any("$count" in stage for stage in pipeline):
            return [{"nb_offres_avec_categorie": 7}]

        return []


class MockStatsRepository:
    """Mock du repository de stats pour les tests"""

    def __init__(self):
        self.saved_stats: List[dict] = []

    async def save_competence_stats(self, stats: dict) -> bool:
        self.saved_stats.append(stats)
        return True

    async def get_latest_stats(self) -> Optional[dict]:
        return self.saved_stats[-1] if self.saved_stats else None


class TestStatsGenerator:
    """Tests pour le service de génération de statistiques"""

    @pytest.fixture
    def sample_referentiel(self):
        """Référentiel de compétences simplifié pour les tests"""
        return {
            "Backend": ["Python", "Django", "FastAPI", "Java", "Spring"],
            "Frontend": ["JavaScript", "React", "Vue", "Angular"],
            "DevOps": ["Docker", "Kubernetes", "CI/CD", "Jenkins"],
        }

    @pytest.fixture
    def sample_jobs(self):
        """Données d'offres simulées"""
        return [
            {
                "source_id": "1",
                "source": "france_travail",
                "competences_extraites": ["Python", "Django", "Docker"],
                "date_collecte": datetime(2024, 12, 15),
            },
            {
                "source_id": "2",
                "source": "france_travail",
                "competences_extraites": ["JavaScript", "React"],
                "date_collecte": datetime(2024, 12, 15),
            },
            {
                "source_id": "3",
                "source": "france_travail",
                "competences_extraites": ["Python", "FastAPI", "Docker", "Kubernetes"],
                "date_collecte": datetime(2024, 12, 16),
            },
        ]

    @pytest.fixture
    def stats_generator(self, sample_jobs, sample_referentiel):
        """Fixture pour le générateur de stats"""
        from backend_v2.domain.services import StatsGenerator

        job_repo = MockJobRepository(sample_jobs)
        stats_repo = MockStatsRepository()

        return StatsGenerator(
            source_name="france_travail",
            job_repository=job_repo,
            stats_repository=stats_repo,
            competences_referentiel=sample_referentiel,
        )

    def test_generate_complete_statistics_success(self, stats_generator):
        """Test génération complète des statistiques"""
        async def _test():
            result = await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            assert result["success"] is True
            assert result["source"] == "france_travail"
            assert result["nb_offres_analysees"] == 3
            assert "top_competences" in result
            assert "statistiques_par_categorie" in result

        asyncio.run(_test())

    def test_top_competences_calculated(self, stats_generator):
        """Test calcul du top des compétences"""
        async def _test():
            result = await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            top_comp = result["top_competences"]
            assert len(top_comp) > 0

            # Vérifier la structure
            first = top_comp[0]
            assert "competence" in first
            assert "nb_occurrences" in first
            assert "pourcentage" in first

        asyncio.run(_test())

    def test_category_statistics_calculated(self, stats_generator):
        """Test calcul des statistiques par catégorie"""
        async def _test():
            result = await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            stats_cat = result["statistiques_par_categorie"]
            assert "Backend" in stats_cat
            assert "Frontend" in stats_cat
            assert "DevOps" in stats_cat

            # Vérifier la structure d'une catégorie
            backend_stats = stats_cat["Backend"]
            assert "nb_offres_avec_categorie" in backend_stats
            assert "pourcentage_offres" in backend_stats
            assert "technologies_populaires" in backend_stats

        asyncio.run(_test())

    def test_statistics_saved_to_repository(self, stats_generator):
        """Test sauvegarde des statistiques"""
        async def _test():
            await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            # Vérifier que les stats ont été sauvegardées
            saved = stats_generator.stats_repo.saved_stats
            assert len(saved) == 1
            assert saved[0]["source"] == "france_travail"

        asyncio.run(_test())

    def test_temporal_evolution_included(self, stats_generator):
        """Test inclusion de l'évolution temporelle"""
        async def _test():
            result = await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline",
                include_temporal=True,
            )

            assert "evolution_temporelle" in result
            assert "repartition_mensuelle" in result

        asyncio.run(_test())

    def test_categories_can_be_excluded(self, stats_generator):
        """Test exclusion des statistiques par catégorie"""
        async def _test():
            result = await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline",
                include_categories=False,
            )

            # Les catégories devraient être vides
            assert result["statistiques_par_categorie"] == {}
            assert result["nb_categories_analysees"] == 0

        asyncio.run(_test())

    def test_get_latest_statistics(self, stats_generator):
        """Test récupération des dernières statistiques"""
        async def _test():
            # Générer d'abord des stats
            await stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            # Récupérer les dernières
            latest = await stats_generator.get_latest_statistics()
            assert latest is not None
            assert latest["source"] == "france_travail"

        asyncio.run(_test())


class TestStatsGeneratorEmptyData:
    """Tests avec données vides"""

    @pytest.fixture
    def empty_stats_generator(self):
        """Générateur avec données vides"""
        from backend_v2.domain.services import StatsGenerator

        job_repo = MockJobRepository([])
        stats_repo = MockStatsRepository()

        return StatsGenerator(
            source_name="france_travail",
            job_repository=job_repo,
            stats_repository=stats_repo,
            competences_referentiel={"Backend": ["Python"]},
        )

    def test_empty_collection_returns_success(self, empty_stats_generator):
        """Test avec collection vide"""
        async def _test():
            result = await empty_stats_generator.generate_complete_statistics(
                pipeline_name="test_pipeline"
            )

            assert result["success"] is True
            assert result["nb_offres_analysees"] == 0
            assert "message" in result
            assert "Aucune offre" in result["message"]

        asyncio.run(_test())
