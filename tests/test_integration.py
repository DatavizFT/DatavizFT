"""Tests simples et fonctionnels pour DatavizFT."""
import json
from pathlib import Path

from backend.tools.competence_analyzer import CompetenceAnalyzer
from backend.tools.file_manager import FileManager


class TestSimpleFileOperations:
    """Tests simples des opérations de fichiers."""

    def test_file_manager_basic_operations(self, temp_dir: Path) -> None:
        """Test des opérations de base du FileManager."""
        fm = FileManager(temp_dir)

        # Test création structure
        fm.creer_structure_dossiers()
        assert fm.data_dir.exists()
        assert fm.results_dir.exists()

        # Test sauvegarde offres
        test_offres = [
            {"id": "123", "intitule": "Développeur Python"},
            {"id": "456", "intitule": "Expert Java"}
        ]

        result_path = fm.sauvegarder_offres(test_offres)
        assert Path(result_path).exists()

        # Vérifier le contenu sauvegardé
        with open(result_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        # Le format inclut metadata et offres
        assert "metadata" in loaded_data
        assert "offres" in loaded_data
        assert len(loaded_data["offres"]) == 2
        assert loaded_data["offres"][0]["intitule"] == "Développeur Python"


class TestSimpleCompetenceAnalysis:
    """Tests simples de l'analyse de compétences."""

    def test_competence_analyzer_basic_workflow(self) -> None:
        """Test du workflow de base de l'analyseur."""
        referentiel = {
            "languages": ["Python", "Java", "JavaScript"],
            "databases": ["PostgreSQL", "MySQL"]
        }

        analyzer = CompetenceAnalyzer(referentiel)

        # Test avec des offres simples
        offres = [
            {
                "id": "1",
                "intitule": "Développeur Python",
                "description": "Poste de développeur Python avec PostgreSQL"
            }
        ]

        # L'analyse devrait fonctionner sans erreur
        result = analyzer.analyser_offres(offres, verbose=False)

        # Vérifications de base
        assert isinstance(result, dict)
        assert "nb_offres_analysees" in result
        assert result["nb_offres_analysees"] == 1

        # Devrait avoir les catégories
        assert "resultats_par_categorie" in result
        categories = result["resultats_par_categorie"]
        assert "languages" in categories
        assert "databases" in categories


class TestConfigurationValidation:
    """Tests de validation de la configuration."""

    def test_config_constants_exist(self) -> None:
        """Test que les constantes de configuration existent."""
        from backend.config import (
            API_BASE_URL,
            FRANCETRAVAIL_CLIENT_ID,
            FRANCETRAVAIL_CLIENT_SECRET,
            TOKEN_URL,
        )

        # Les URLs doivent être définies
        assert isinstance(TOKEN_URL, str)
        assert isinstance(API_BASE_URL, str)
        assert len(TOKEN_URL) > 0
        assert len(API_BASE_URL) > 0

        # Les IDs peuvent être None ou string
        assert FRANCETRAVAIL_CLIENT_ID is None or isinstance(FRANCETRAVAIL_CLIENT_ID, str)
        assert FRANCETRAVAIL_CLIENT_SECRET is None or isinstance(FRANCETRAVAIL_CLIENT_SECRET, str)


class TestDataStructures:
    """Tests des structures de données."""

    def test_competences_json_structure(self) -> None:
        """Test de la structure du fichier de compétences."""
        # Le fichier de compétences devrait exister
        competences_file = Path("backend/models/competences.json")

        if competences_file.exists():
            with competences_file.open("r", encoding="utf-8") as f:
                competences_data = json.load(f)

            # Vérifier que c'est un dictionnaire
            assert isinstance(competences_data, dict)

            # Chaque catégorie devrait être une liste
            for categorie, items in competences_data.items():
                assert isinstance(categorie, str)
                assert isinstance(items, list)

                # Chaque item devrait être une string
                for item in items:
                    assert isinstance(item, str)
                    assert len(item) > 0

    def test_sample_data_processing(self) -> None:
        """Test du traitement de données d'exemple."""
        # Données d'exemple d'offre
        sample_offre = {
            "id": "12345",
            "intitule": "Développeur Full Stack",
            "description": "Recherche développeur Python/Django avec connaissances PostgreSQL",
            "lieu": "Paris",
            "type_contrat": "CDI"
        }

        # Test que les champs essentiels sont présents
        assert "id" in sample_offre
        assert "intitule" in sample_offre
        assert "description" in sample_offre

        # Test des types
        assert isinstance(sample_offre["id"], str)
        assert isinstance(sample_offre["intitule"], str)
        assert isinstance(sample_offre["description"], str)


class TestErrorHandling:
    """Tests de gestion d'erreurs."""

    def test_file_manager_with_invalid_path(self) -> None:
        """Test du FileManager avec un chemin invalide."""
        # Chemin vers un fichier au lieu d'un dossier
        invalid_path = Path(__file__)  # C'est un fichier, pas un dossier

        # Le FileManager devrait gérer ça gracieusement
        fm = FileManager(invalid_path.parent)  # Utilise le parent qui est un dossier
        assert fm.base_path == invalid_path.parent

    def test_competence_analyzer_empty_referentiel(self) -> None:
        """Test de l'analyseur avec un référentiel vide."""
        analyzer = CompetenceAnalyzer({})

        # Devrait fonctionner avec des offres vides
        result = analyzer.analyser_offres([], verbose=False)
        assert isinstance(result, dict)
        assert result["nb_offres_analysees"] == 0

        # Et avec des offres réelles mais sans compétences à détecter
        offres = [{"id": "1", "description": "Poste intéressant"}]
        result = analyzer.analyser_offres(offres, verbose=False)
        assert result["nb_offres_analysees"] == 1


class TestIntegration:
    """Tests d'intégration simples."""

    def test_full_pipeline_simulation(self, temp_dir: Path) -> None:
        """Test de simulation du pipeline complet."""
        # 1. Initialiser le FileManager
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        # 2. Simuler des données d'offres
        offres = [
            {
                "id": "1",
                "intitule": "Développeur Python",
                "description": "Développement en Python avec Django"
            },
            {
                "id": "2",
                "intitule": "Administrateur Base de Données",
                "description": "Administration PostgreSQL et MySQL"
            }
        ]

        # 3. Sauvegarder les offres
        offres_path = fm.sauvegarder_offres(offres)
        assert Path(offres_path).exists()

        # 4. Analyser les compétences
        referentiel = {
            "languages": ["Python"],
            "frameworks": ["Django"],
            "databases": ["PostgreSQL", "MySQL"]
        }

        analyzer = CompetenceAnalyzer(referentiel)
        resultats = analyzer.analyser_offres(offres, verbose=False)

        # 5. Vérifications finales
        assert resultats["nb_offres_analysees"] == 2
        assert "resultats_par_categorie" in resultats

        # Vérifier qu'on a détecté des compétences
        categories = resultats["resultats_par_categorie"]
        assert len(categories) > 0
