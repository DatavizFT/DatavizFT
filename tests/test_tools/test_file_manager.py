"""Tests pour le gestionnaire de fichiers."""
import json
from pathlib import Path
from unittest.mock import patch

from backend.tools.file_manager import FileManager


class TestFileManager:
    """Tests pour FileManager."""

    def test_init_default(self) -> None:
        """Test l'initialisation par défaut."""
        fm = FileManager()
        assert fm.base_path is not None
        assert fm.base_path.exists()
        assert fm.data_dir == fm.base_path / "data"
        assert fm.results_dir == fm.data_dir / "json_results"

    def test_init_custom_path(self, temp_dir: Path) -> None:
        """Test l'initialisation avec un chemin personnalisé."""
        fm = FileManager(temp_dir)
        assert fm.base_path == temp_dir
        assert fm.data_dir == temp_dir / "data"
        assert fm.results_dir == temp_dir / "data" / "json_results"

    def test_creer_structure_dossiers(self, temp_dir: Path, capsys) -> None:
        """Test de création de la structure de dossiers."""
        fm = FileManager(temp_dir)

        # Les dossiers ne devraient pas exister au début
        assert not fm.data_dir.exists()
        assert not fm.results_dir.exists()

        fm.creer_structure_dossiers()

        # Maintenant ils devraient exister
        assert fm.data_dir.exists()
        assert fm.results_dir.exists()

        # Vérifier le message de confirmation
        captured = capsys.readouterr()
        assert "Structure de dossiers créée" in captured.out

    def test_creer_structure_dossiers_existing(self, temp_dir: Path) -> None:
        """Test de création quand les dossiers existent déjà."""
        fm = FileManager(temp_dir)

        # Créer les dossiers manuellement
        fm.data_dir.mkdir(parents=True)
        fm.results_dir.mkdir(parents=True)

        # Créer la structure ne devrait pas lever d'erreur
        fm.creer_structure_dossiers()

        # Les dossiers devraient toujours exister
        assert fm.data_dir.exists()
        assert fm.results_dir.exists()

    @patch('backend.tools.file_manager.nettoyer_offres_pour_json')
    def test_sauvegarder_offres(self, mock_nettoyer, temp_dir: Path, capsys) -> None:
        """Test de sauvegarde des offres."""
        # Configuration du mock
        test_offres = [{"id": "1", "intitule": "Dev"}]
        mock_nettoyer.return_value = test_offres

        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        result_path = fm.sauvegarder_offres(test_offres, "M1805")

        # Vérifier que le fichier a été créé
        assert Path(result_path).exists()
        assert "M1805" in result_path
        assert result_path.endswith(".json")

        # Vérifier que le nettoyage a été appelé
        mock_nettoyer.assert_called_once_with(test_offres)

        # Vérifier le message de confirmation
        captured = capsys.readouterr()
        assert "offres sauvegardées" in captured.out

    def test_sauvegarder_resultats_analyse(self, temp_dir: Path, capsys) -> None:
        """Test de sauvegarde des résultats d'analyse."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        test_resultats = {
            "total_competences": 10,
            "categories": {"languages": 5, "frameworks": 3}
        }

        result_path = fm.sauvegarder_resultats_analyse(test_resultats, "M1805")

        # Vérifier que le fichier a été créé
        assert Path(result_path).exists()
        assert "analyse_competences_M1805" in result_path

        # Vérifier le contenu
        with open(result_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == test_resultats

        # Vérifier le message
        captured = capsys.readouterr()
        assert "Résultats d'analyse sauvegardés" in captured.out

    def test_charger_competences_json_existing_file(self, temp_dir: Path) -> None:
        """Test du chargement d'un fichier de compétences existant."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        # Créer un fichier de compétences de test
        test_data = {"python": {"type": "language", "level": "expert"}}
        competences_file = fm.data_dir / "competences_test.json"

        with competences_file.open("w", encoding="utf-8") as f:
            json.dump(test_data, f)

        loaded_data = fm.charger_competences_json("competences_test.json")
        assert loaded_data == test_data

    def test_charger_competences_json_missing_file(self, temp_dir: Path, capsys) -> None:
        """Test du chargement d'un fichier manquant."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        result = fm.charger_competences_json("missing_file.json")

        # Devrait retourner un dict vide
        assert result == {}

        # Devrait afficher un message d'erreur
        captured = capsys.readouterr()
        assert "Erreur" in captured.out and "missing_file.json" in captured.out

    def test_lister_fichiers_json(self, temp_dir: Path) -> None:
        """Test du listage des fichiers JSON."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        # Créer quelques fichiers de test
        (fm.data_dir / "test1.json").touch()
        (fm.data_dir / "test2.json").touch()
        (fm.data_dir / "test.txt").touch()  # Pas JSON

        json_files = fm.lister_fichiers_json()

        # Devrait retourner seulement les fichiers JSON
        assert len(json_files) == 2
        assert all(f.suffix == ".json" for f in json_files)
        assert any("test1.json" in str(f) for f in json_files)
        assert any("test2.json" in str(f) for f in json_files)

    def test_supprimer_fichier_existing(self, temp_dir: Path) -> None:
        """Test de suppression d'un fichier existant."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        # Créer un fichier de test
        test_file = fm.data_dir / "to_delete.json"
        test_file.write_text('{"test": true}')

        assert test_file.exists()

        success = fm.supprimer_fichier("to_delete.json")

        assert success is True
        assert not test_file.exists()

    def test_supprimer_fichier_missing(self, temp_dir: Path) -> None:
        """Test de suppression d'un fichier manquant."""
        fm = FileManager(temp_dir)
        fm.creer_structure_dossiers()

        success = fm.supprimer_fichier("missing_file.json")
        assert success is False
