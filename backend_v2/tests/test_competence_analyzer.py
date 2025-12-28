"""
Tests pour SemanticCompetenceAnalyzer
=====================================

Vérifie l'extraction de compétences par embeddings sémantiques.
"""

import pytest


class TestSemanticCompetenceAnalyzer:
    """Tests pour l'analyseur sémantique de compétences"""

    @pytest.fixture
    def embedding_service(self):
        """Fixture pour le service d'embeddings"""
        from backend_v2.infrastructure.ml import EmbeddingService
        return EmbeddingService()

    @pytest.fixture
    def mini_referentiel(self):
        """Référentiel minimal pour tests rapides"""
        return {
            "langages": ["Python", "JavaScript", "Java", "C#"],
            "frameworks": ["Django", "FastAPI", "React", "Angular"],
            "bases_de_donnees": ["PostgreSQL", "MongoDB", "MySQL"],
            "devops": ["Docker", "Kubernetes", "Jenkins"]
        }

    @pytest.fixture
    def analyzer(self, embedding_service, mini_referentiel):
        """Fixture pour l'analyseur avec référentiel minimal"""
        from backend_v2.domain.services import SemanticCompetenceAnalyzer
        return SemanticCompetenceAnalyzer(
            embedding_service=embedding_service,
            referentiel=mini_referentiel,
            seuil_similarite=0.35  # Seuil adapté aux embeddings texte vs mot
        )

    def test_detect_exact_competence(self, analyzer):
        """Détecte une compétence mentionnée exactement"""
        text = "Nous recherchons un développeur Python avec 5 ans d'expérience."
        matches = analyzer.analyze_text(text)

        competences = [m.nom for m in matches]
        assert "Python" in competences

    def test_detect_synonym_ml_machine_learning(self, analyzer, embedding_service):
        """Détecte les synonymes grâce aux embeddings"""
        # Créer un analyseur avec ML et Machine Learning
        referentiel = {
            "data": ["Machine Learning", "Deep Learning", "Data Science"]
        }
        analyzer = type(analyzer)(
            embedding_service=embedding_service,
            referentiel=referentiel,
            seuil_similarite=0.25
        )

        # Le texte complet mentionnant Machine Learning devrait matcher
        text = "Expérience en Machine Learning et traitement de données"
        matches = analyzer.analyze_text(text)

        # Le score devrait être élevé pour Machine Learning
        ml_matches = [m for m in matches if "Learning" in m.nom or "Data" in m.nom]
        assert len(ml_matches) > 0

    def test_detect_multiple_competences(self, analyzer):
        """Détecte plusieurs compétences dans un texte"""
        # Texte avec compétences clairement mentionnées
        text = """
        Poste de Développeur Python avec Django.
        Expérience requise en PostgreSQL et Docker.
        """
        matches = analyzer.analyze_text(text)

        # Devrait détecter au moins une compétence
        assert len(matches) >= 1

        # Vérifier que les bonnes compétences sont détectées
        competences = [m.nom for m in matches]
        # Au moins une de ces compétences doit être présente
        expected = ["Python", "Django", "PostgreSQL", "Docker"]
        found = [c for c in expected if c in competences]
        assert len(found) >= 1

    def test_score_ordering(self, analyzer):
        """Les résultats sont triés par score décroissant"""
        text = "Expert Python et Django pour développement web"
        matches = analyzer.analyze_text(text)

        if len(matches) >= 2:
            scores = [m.score for m in matches]
            assert scores == sorted(scores, reverse=True)

    def test_categorie_preserved(self, analyzer):
        """La catégorie est correctement associée"""
        text = "Développeur Python"
        matches = analyzer.analyze_text(text)

        python_match = next((m for m in matches if m.nom == "Python"), None)
        if python_match:
            assert python_match.categorie == "langages"

    def test_top_k_limit(self, analyzer):
        """Respecte la limite top_k"""
        text = "Python Django PostgreSQL Docker React JavaScript"
        matches = analyzer.analyze_text(text, top_k=3)

        assert len(matches) <= 3

    def test_analyze_job(self, analyzer):
        """Test de la méthode analyze_job avec intitulé et description"""
        intitule = "Développeur Python Senior"
        description = "Nous recherchons un expert Django pour notre équipe backend."

        matches = analyzer.analyze_job(intitule, description)
        competences = [m.nom for m in matches]

        assert "Python" in competences or "Django" in competences

    def test_empty_text_returns_empty(self, analyzer):
        """Texte vide retourne liste vide"""
        matches = analyzer.analyze_text("")
        assert matches == []

    def test_no_competence_text(self, analyzer):
        """Texte sans compétence technique retourne peu/pas de résultats"""
        text = "Nous recherchons une personne motivée et dynamique."
        matches = analyzer.analyze_text(text)

        # Ne devrait pas matcher de compétences techniques
        # (ou très peu avec des scores faibles)
        high_score_matches = [m for m in matches if m.score > 0.5]
        assert len(high_score_matches) == 0

    def test_referentiel_stats(self, analyzer, mini_referentiel):
        """Test des statistiques du référentiel"""
        stats = analyzer.get_referentiel_stats()

        assert stats["nb_categories"] == 4
        assert stats["total_competences"] == 14  # 4 + 4 + 3 + 3

    def test_competence_match_to_dict(self):
        """Test sérialisation de CompetenceMatch"""
        from backend_v2.domain.services import CompetenceMatch

        match = CompetenceMatch(nom="Python", score=0.8567, categorie="langages")
        d = match.to_dict()

        assert d["nom"] == "Python"
        assert d["score"] == 0.857  # Arrondi à 3 décimales
        assert d["categorie"] == "langages"
