"""
Tests pour DeduplicationService
================================

Vérifie la détection de doublons sémantiques.
"""

import pytest
import numpy as np
from datetime import datetime


class TestDeduplicationService:
    """Tests pour le service de déduplication"""

    @pytest.fixture
    def embedding_service(self):
        """Fixture pour le service d'embeddings"""
        from backend_v2.infrastructure.ml import EmbeddingService
        return EmbeddingService()

    @pytest.fixture
    def dedup_service(self, embedding_service):
        """Fixture pour le service de déduplication"""
        from backend_v2.domain.services import DeduplicationService
        return DeduplicationService(
            embedding_service=embedding_service,
            seuil_doublon=0.95
        )

    @pytest.fixture
    def sample_job(self):
        """Fixture pour créer un job de test"""
        from backend_v2.domain.entities.job import Job

        def _create_job(source_id: str, intitule: str, description: str):
            return Job(
                source_id=source_id,
                intitule=intitule,
                description=description,
                date_creation=datetime.now(),
                date_actualisation=None,
                lieu_travail={"libelle": "Paris"},
                entreprise={"nom": "Test Company"},
                agence={},
                type_contrat="CDI",
                type_contrat_libelle="Contrat à durée indéterminée",
                qualification_code="9",
                qualification_libelle="Cadre",
                code_NAF="6201Z",
                nature_contrat="Contrat travail",
                source="test"
            )
        return _create_job

    def test_identical_jobs_are_duplicates(self, dedup_service, sample_job, embedding_service):
        """Offres identiques sont détectées comme doublons"""
        job1 = sample_job("1", "Développeur Python", "Expert Python Django PostgreSQL")
        job2 = sample_job("2", "Développeur Python", "Expert Python Django PostgreSQL")

        # Calculer l'embedding du premier job
        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(job2, existing)

        assert is_dup is True
        assert score > 0.99

    def test_similar_jobs_detected(self, dedup_service, sample_job, embedding_service):
        """Offres très similaires sont détectées"""
        job1 = sample_job(
            "1",
            "Développeur Python Senior",
            "Nous recherchons un développeur Python expérimenté pour notre équipe."
        )
        job2 = sample_job(
            "2",
            "Senior Python Developer",
            "We are looking for an experienced Python developer for our team."
        )

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(job2, existing)

        # Même sens, langue différente - devrait être détecté avec seuil ajusté
        assert score > 0.7  # Score élevé même si pas 0.95

    def test_different_jobs_not_duplicates(self, dedup_service, sample_job, embedding_service):
        """Offres différentes ne sont pas des doublons"""
        job1 = sample_job(
            "1",
            "Développeur Python",
            "Expert en Django et FastAPI pour backend web"
        )
        job2 = sample_job(
            "2",
            "Boulanger",
            "Préparation de pains et viennoiseries"
        )

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(job2, existing)

        assert is_dup is False
        assert score < 0.5

    def test_empty_existing_not_duplicate(self, dedup_service, sample_job):
        """Première offre n'est jamais un doublon"""
        job = sample_job("1", "Test", "Description test")
        empty_embeddings = np.empty((0, 512))

        is_dup, score = dedup_service.is_duplicate(job, empty_embeddings)

        assert is_dup is False
        assert score is None

    def test_find_duplicates_in_batch(self, dedup_service, sample_job):
        """Test filtrage des doublons dans un batch"""
        jobs = [
            sample_job("1", "Dev Python", "Expert Python Django"),
            sample_job("2", "Dev Python", "Expert Python Django"),  # Doublon de 1
            sample_job("3", "Dev Java", "Expert Java Spring Boot"),
            sample_job("4", "Dev Python", "Expert Python Django"),  # Doublon de 1
        ]

        unique, duplicates, _ = dedup_service.find_duplicates_in_batch(jobs)

        # 1 et 3 sont uniques, 2 et 4 sont des doublons
        assert len(unique) == 2
        assert len(duplicates) == 2

    def test_embeddings_stored_in_jobs(self, dedup_service, sample_job):
        """Vérifie que les embeddings sont stockés dans les jobs uniques"""
        jobs = [
            sample_job("1", "Dev Python", "Expert Python"),
            sample_job("2", "Dev Java", "Expert Java"),
        ]

        unique, _, _ = dedup_service.find_duplicates_in_batch(jobs)

        for job in unique:
            assert job.embedding is not None
            assert isinstance(job.embedding, list)
            assert len(job.embedding) > 0

    def test_find_similar_jobs(self, dedup_service, sample_job):
        """Test recherche d'offres similaires"""
        reference = sample_job("1", "Dev Python Senior", "Expert Django FastAPI")
        candidates = [
            sample_job("2", "Dev Python Junior", "Développeur Python débutant"),
            sample_job("3", "Dev Java", "Expert Spring Boot"),
            sample_job("4", "Dev Python", "Spécialiste Django REST"),
        ]

        similar = dedup_service.find_similar_jobs(
            reference,
            candidates,
            top_k=2,
            min_similarity=0.3
        )

        assert len(similar) <= 2
        # Les résultats Python devraient être plus proches que Java
        if len(similar) >= 2:
            # Vérifier que les scores sont décroissants
            assert similar[0][1] >= similar[1][1]

    def test_compute_similarity_matrix(self, dedup_service, sample_job):
        """Test calcul de la matrice de similarité"""
        jobs = [
            sample_job("1", "Dev Python", "Expert Python"),
            sample_job("2", "Dev Python", "Développeur Python"),
            sample_job("3", "Dev Java", "Expert Java"),
        ]

        matrix = dedup_service.compute_similarity_matrix(jobs)

        assert matrix.shape == (3, 3)
        # Diagonale = 1 (même job)
        for i in range(3):
            assert matrix[i][i] > 0.99
        # Python vs Python > Python vs Java
        assert matrix[0][1] > matrix[0][2]


class TestMetadataPreFiltering:
    """Tests pour le pré-filtrage par métadonnées (entreprise, ville)"""

    @pytest.fixture
    def embedding_service(self):
        from backend_v2.infrastructure.ml import EmbeddingService
        return EmbeddingService()

    @pytest.fixture
    def dedup_service(self, embedding_service):
        from backend_v2.domain.services import DeduplicationService
        return DeduplicationService(
            embedding_service=embedding_service,
            seuil_doublon=0.95
        )

    @pytest.fixture
    def job_factory(self):
        """Factory pour créer des jobs avec entreprise et ville personnalisées"""
        from backend_v2.domain.entities.job import Job

        def _create_job(
            source_id: str,
            intitule: str,
            description: str,
            entreprise_nom: str = "Test Company",
            ville: str = "Paris"
        ):
            return Job(
                source_id=source_id,
                intitule=intitule,
                description=description,
                date_creation=datetime.now(),
                date_actualisation=None,
                lieu_travail={"libelle": ville},
                entreprise={"nom": entreprise_nom},
                agence={},
                type_contrat="CDI",
                type_contrat_libelle="Contrat à durée indéterminée",
                qualification_code="9",
                qualification_libelle="Cadre",
                code_NAF="6201Z",
                nature_contrat="Contrat travail",
                source="test"
            )
        return _create_job

    def test_different_company_not_duplicate(self, dedup_service, job_factory, embedding_service):
        """Offres avec entreprises différentes ne sont pas des doublons"""
        job1 = job_factory("1", "Dev Python", "Expert Python Django", "Google", "Paris")
        job2 = job_factory("2", "Dev Python", "Expert Python Django", "Microsoft", "Paris")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        # Avec pré-filtrage activé (existing_jobs fourni)
        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # Entreprise différente → pas un doublon (même si description identique)
        assert is_dup is False
        assert score is None  # Pas de comparaison sémantique effectuée

    def test_different_city_not_duplicate(self, dedup_service, job_factory, embedding_service):
        """Offres avec villes différentes ne sont pas des doublons"""
        job1 = job_factory("1", "Dev Python", "Expert Python Django", "Google", "Paris")
        job2 = job_factory("2", "Dev Python", "Expert Python Django", "Google", "Lyon")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # Ville différente → pas un doublon
        assert is_dup is False
        assert score is None

    def test_same_metadata_checks_semantic(self, dedup_service, job_factory, embedding_service):
        """Offres avec mêmes métadonnées passent à la comparaison sémantique"""
        job1 = job_factory("1", "Dev Python", "Expert Python Django", "Google", "Paris")
        job2 = job_factory("2", "Dev Python", "Expert Python Django", "Google", "Paris")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # Même entreprise + même ville → comparaison sémantique
        assert is_dup is True
        assert score is not None
        assert score > 0.99

    def test_empty_company_does_semantic_check(self, dedup_service, job_factory, embedding_service):
        """Si l'entreprise est vide, on fait la comparaison sémantique par sécurité"""
        job1 = job_factory("1", "Dev Python", "Expert Python Django", "", "Paris")
        job2 = job_factory("2", "Dev Python", "Expert Python Django", "Google", "Paris")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # Entreprise vide → on ne peut pas exclure, donc comparaison sémantique
        assert score is not None
        assert score > 0.99

    def test_batch_with_different_companies(self, dedup_service, job_factory):
        """Test batch avec entreprises différentes - pas de doublons"""
        jobs = [
            job_factory("1", "Dev Python", "Expert Python Django", "Google", "Paris"),
            job_factory("2", "Dev Python", "Expert Python Django", "Microsoft", "Paris"),
            job_factory("3", "Dev Python", "Expert Python Django", "Amazon", "Paris"),
        ]

        unique, duplicates, _ = dedup_service.find_duplicates_in_batch(jobs)

        # 3 entreprises différentes → 3 offres uniques
        assert len(unique) == 3
        assert len(duplicates) == 0

    def test_batch_with_same_company_different_cities(self, dedup_service, job_factory):
        """Test batch avec même entreprise mais villes différentes"""
        jobs = [
            job_factory("1", "Dev Python", "Expert Python Django", "Google", "Paris"),
            job_factory("2", "Dev Python", "Expert Python Django", "Google", "Lyon"),
            job_factory("3", "Dev Python", "Expert Python Django", "Google", "Marseille"),
        ]

        unique, duplicates, _ = dedup_service.find_duplicates_in_batch(jobs)

        # Même entreprise, villes différentes → 3 offres uniques
        assert len(unique) == 3
        assert len(duplicates) == 0

    def test_normalization_case_insensitive(self, dedup_service, job_factory, embedding_service):
        """Le pré-filtrage est insensible à la casse"""
        job1 = job_factory("1", "Dev Python", "Expert Python", "GOOGLE", "PARIS")
        job2 = job_factory("2", "Dev Python", "Expert Python", "google", "paris")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # GOOGLE == google, PARIS == paris → doublon
        assert is_dup is True
        assert score > 0.99

    def test_normalization_accents(self, dedup_service, job_factory, embedding_service):
        """Le pré-filtrage normalise les accents"""
        job1 = job_factory("1", "Dev Python", "Expert Python", "Société Générale", "Évry")
        job2 = job_factory("2", "Dev Python", "Expert Python", "Societe Generale", "Evry")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # Accents normalisés → doublon
        assert is_dup is True
        assert score > 0.99

    def test_city_extraction_from_libelle(self, dedup_service, job_factory, embedding_service):
        """Extraction correcte de la ville depuis le format '75 - Paris'"""
        from backend_v2.domain.entities.job import Job

        job1 = Job(
            source_id="1",
            intitule="Dev Python",
            description="Expert Python",
            date_creation=datetime.now(),
            date_actualisation=None,
            lieu_travail={"libelle": "75 - Paris"},
            entreprise={"nom": "Google"},
            agence={},
            type_contrat="CDI",
            type_contrat_libelle="CDI",
            qualification_code="9",
            qualification_libelle="Cadre",
            code_NAF="6201Z",
            nature_contrat="Contrat travail",
            source="test"
        )
        job2 = job_factory("2", "Dev Python", "Expert Python", "Google", "Paris")

        job1_embedding = embedding_service.encode(f"{job1.intitule}\n\n{job1.description}")
        existing_embeddings = np.array([job1_embedding])

        is_dup, score = dedup_service.is_duplicate(
            job2, existing_embeddings, existing_jobs=[job1]
        )

        # "75 - Paris" devrait matcher "Paris"
        assert is_dup is True
        assert score > 0.99
