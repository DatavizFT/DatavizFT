"""
Tests pour EmbeddingService
===========================

Vérifie le bon fonctionnement du service d'embeddings sémantiques.
"""

import pytest
import numpy as np


class TestEmbeddingService:
    """Tests pour le service d'embeddings"""

    @pytest.fixture
    def embedding_service(self):
        """Fixture pour le service d'embeddings (singleton)"""
        from backend_v2.infrastructure.ml import EmbeddingService
        return EmbeddingService()

    def test_singleton_pattern(self, embedding_service):
        """Vérifie que le service est bien un singleton"""
        from backend_v2.infrastructure.ml import EmbeddingService
        service2 = EmbeddingService()
        assert embedding_service is service2

    def test_encode_single_text(self, embedding_service):
        """Test encodage d'un texte unique"""
        text = "Développeur Python senior"
        embedding = embedding_service.encode(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.ndim == 1  # Vecteur 1D
        assert len(embedding) > 0

    def test_encode_multiple_texts(self, embedding_service):
        """Test encodage batch de plusieurs textes"""
        texts = [
            "Développeur Python",
            "Ingénieur DevOps",
            "Data Scientist"
        ]
        embeddings = embedding_service.encode(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3  # 3 textes
        assert embeddings.ndim == 2  # Matrice 2D

    def test_similarity_identical_texts(self, embedding_service):
        """Textes identiques doivent avoir similarité proche de 1"""
        text = "Développeur Python expérimenté"
        e1 = embedding_service.encode(text)
        e2 = embedding_service.encode(text)

        similarity = embedding_service.similarity(e1, e2)
        assert similarity > 0.99

    def test_similarity_similar_texts(self, embedding_service):
        """Textes similaires doivent avoir haute similarité"""
        e1 = embedding_service.encode("Développeur Python senior")
        e2 = embedding_service.encode("Senior Python Developer")

        similarity = embedding_service.similarity(e1, e2)
        assert similarity > 0.7  # Même concept, langues différentes

    def test_similarity_different_texts(self, embedding_service):
        """Textes différents doivent avoir faible similarité"""
        e1 = embedding_service.encode("Développeur Python")
        e2 = embedding_service.encode("Boulanger pâtissier")

        similarity = embedding_service.similarity(e1, e2)
        assert similarity < 0.5

    def test_batch_similarity(self, embedding_service):
        """Test calcul de similarité batch"""
        query = embedding_service.encode("Python")
        candidates = embedding_service.encode([
            "Python programming",
            "Java development",
            "Data science with Python"
        ])

        similarities = embedding_service.batch_similarity(query, candidates)

        assert len(similarities) == 3
        # Python devrait être plus proche de "Python programming" et "Data science with Python"
        assert similarities[0] > similarities[1]  # Python prog > Java
        assert similarities[2] > similarities[1]  # Python data > Java

    def test_is_loaded(self, embedding_service):
        """Test vérification du chargement du modèle"""
        # Forcer le chargement
        embedding_service.preload()
        assert embedding_service.is_loaded()

    def test_empty_text(self, embedding_service):
        """Test avec texte vide"""
        embedding = embedding_service.encode("")
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0
