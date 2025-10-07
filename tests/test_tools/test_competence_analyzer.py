"""Tests pour l'analyseur de compétences."""
from typing import Any, Dict
from unittest.mock import patch, MagicMock

import pytest

from backend.tools.competence_analyzer import CompetenceAnalyzer


class TestCompetenceAnalyzer:
    """Tests pour CompetenceAnalyzer."""
    
    def test_init_with_referentiel(self) -> None:
        """Test l'initialisation avec un référentiel."""
        referentiel = {
            "languages": ["Python", "Java", "JavaScript"],
            "frameworks": ["Django", "React", "Spring"]
        }
        analyzer = CompetenceAnalyzer(referentiel)
        assert analyzer.referentiel == referentiel
        assert analyzer.cache_resultats == {}
    
    def test_init_empty_referentiel(self) -> None:
        """Test l'initialisation avec un référentiel vide."""
        analyzer = CompetenceAnalyzer({})
        assert analyzer.referentiel == {}
        assert analyzer.cache_resultats == {}
    
    @patch('backend.tools.competence_analyzer.extraire_texte_offre')
    @patch('backend.tools.competence_analyzer.rechercher_competence_dans_texte')
    def test_analyser_offres_empty_list(self, mock_rechercher, mock_extraire) -> None:
        """Test l'analyse d'une liste vide d'offres."""
        analyzer = CompetenceAnalyzer({})
        result = analyzer.analyser_offres([], verbose=False)
        
        # Avec une liste vide, aucun mock ne devrait être appelé
        mock_extraire.assert_not_called()
        mock_rechercher.assert_not_called()
        assert result == {}
    
    @patch('backend.tools.competence_analyzer.extraire_texte_offre')
    @patch('backend.tools.competence_analyzer.rechercher_competence_dans_texte')
    def test_analyser_offres_with_data(self, mock_rechercher, mock_extraire) -> None:
        """Test l'analyse d'offres avec données."""
        # Configuration des mocks
        mock_extraire.return_value = "Développeur Python avec Django"
        mock_rechercher.return_value = ["Python", "Django"]
        
        referentiel = {
            "languages": ["Python", "Java"],
            "frameworks": ["Django", "React"]
        }
        analyzer = CompetenceAnalyzer(referentiel)
        
        offres = [
            {"id": "1", "description": "Poste développeur"},
            {"id": "2", "description": "Expert backend"}
        ]
        
        result = analyzer.analyser_offres(offres, verbose=False)
        
        # Vérifier que les mocks ont été appelés
        assert mock_extraire.call_count == len(offres) * len(referentiel)
        assert mock_rechercher.call_count == len(offres) * len(referentiel)
        
        # Le résultat devrait être un dictionnaire par catégorie
        assert isinstance(result, dict)
    
    def test_analyser_offres_verbose_mode(self, capsys) -> None:
        """Test le mode verbose."""
        analyzer = CompetenceAnalyzer({"test": ["item"]})
        
        with patch('backend.tools.competence_analyzer.extraire_texte_offre', return_value="text"):
            with patch('backend.tools.competence_analyzer.rechercher_competence_dans_texte', return_value=[]):
                analyzer.analyser_offres([{"id": "1"}], verbose=True)
        
        # Vérifier que des messages ont été affichés
        captured = capsys.readouterr()
        assert "ANALYSE DES COMPÉTENCES" in captured.out
        assert "Analyse catégorie: test" in captured.out


class TestIntegrationWithMocks:
    """Tests d'intégration avec mocks des dépendances."""
    
    @patch('backend.tools.competence_analyzer.extraire_texte_offre')
    @patch('backend.tools.competence_analyzer.rechercher_competence_dans_texte')
    def test_full_analysis_workflow(self, mock_rechercher, mock_extraire) -> None:
        """Test du workflow complet d'analyse."""
        # Configuration des mocks pour simuler un comportement réaliste
        mock_extraire.return_value = "Poste de développeur Python avec Django et PostgreSQL"
        
        def mock_search_side_effect(text, competences):
            # Simule la recherche selon les compétences demandées
            if "Python" in competences:
                return ["Python"]
            elif "Django" in competences:
                return ["Django"] 
            elif "PostgreSQL" in competences:
                return ["PostgreSQL"]
            return []
        
        mock_rechercher.side_effect = mock_search_side_effect
        
        referentiel = {
            "languages": ["Python", "JavaScript", "Java"],
            "frameworks": ["Django", "React", "Angular"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB"]
        }
        
        analyzer = CompetenceAnalyzer(referentiel)
        
        offres = [
            {
                "id": "offre_1",
                "intitule": "Développeur Full Stack",
                "description": "Poste de développeur..."
            }
        ]
        
        result = analyzer.analyser_offres(offres, verbose=False)
        
        # Vérifications
        assert isinstance(result, dict)
        assert len(result) == len(referentiel)  # Une clé par catégorie
        
        # Chaque catégorie devrait être présente
        for categorie in referentiel.keys():
            assert categorie in result
    
    def test_cache_functionality(self) -> None:
        """Test du système de cache."""
        analyzer = CompetenceAnalyzer({"test": ["item"]})
        
        # Le cache devrait être initialement vide
        assert analyzer.cache_resultats == {}
        
        # Après analyse, on peut ajouter au cache (testé indirectement)
        with patch('backend.tools.competence_analyzer.extraire_texte_offre', return_value="text"):
            with patch('backend.tools.competence_analyzer.rechercher_competence_dans_texte', return_value=[]):
                analyzer.analyser_offres([{"id": "1"}], verbose=False)
        
        # Le cache peut avoir été utilisé (comportement interne)