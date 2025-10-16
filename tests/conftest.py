"""Configuration et fixtures pour les tests."""
import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Crée un dossier temporaire pour les tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_competences_data() -> dict[str, Any]:
    """Données d'exemple pour les tests de compétences."""
    return {
        "competences": [
            {
                "libelle": "Python",
                "code": "COMP_001",
                "type": "technique",
                "niveau": "expert"
            },
            {
                "libelle": "SQL",
                "code": "COMP_002",
                "type": "technique",
                "niveau": "avancé"
            }
        ],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "total_count": 2
        }
    }


@pytest.fixture
def sample_offre_data() -> dict[str, Any]:
    """Données d'exemple d'offre France Travail."""
    return {
        "id": "123456789",
        "intitule": "Développeur Python",
        "description": "Développement d'applications en Python",
        "lieuTravail": {
            "libelle": "Paris 75001",
            "commune": "75101"
        },
        "typeContrat": "CDI",
        "experienceLibelle": "Débutant accepté",
        "competences": [
            {
                "code": "120810",
                "libelle": "Python (langage)"
            }
        ]
    }


@pytest.fixture
def mock_france_travail_client() -> Mock:
    """Mock du client France Travail."""
    mock_client = Mock()
    mock_client.get_offres.return_value = {
        "resultats": [
            {
                "id": "123456789",
                "intitule": "Développeur Python"
            }
        ],
        "filtresPossibles": [],
        "range": {
            "max": 1,
            "min": 0
        }
    }
    return mock_client


@pytest.fixture
def sample_json_file(temp_dir: Path, sample_competences_data: dict[str, Any]) -> Path:
    """Crée un fichier JSON temporaire avec des données d'exemple."""
    json_file = temp_dir / "sample_data.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(sample_competences_data, f, ensure_ascii=False, indent=2)
    return json_file
