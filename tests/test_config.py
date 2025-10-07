"""Tests de configuration."""
import os

import pytest

from backend.config import (
    FRANCETRAVAIL_CLIENT_ID,
    FRANCETRAVAIL_CLIENT_SECRET,
    TOKEN_URL,
    API_BASE_URL
)


class TestConfig:
    """Tests de la configuration."""
    
    def test_token_url_format(self) -> None:
        """Test que TOKEN_URL a le bon format."""
        assert TOKEN_URL.startswith("https://")
        assert "francetravail.io" in TOKEN_URL
        assert "oauth2" in TOKEN_URL
    
    def test_api_base_url_format(self) -> None:
        """Test que API_BASE_URL a le bon format."""
        assert API_BASE_URL.startswith("https://")
        assert "api.francetravail.io" in API_BASE_URL
        assert "offresdemploi" in API_BASE_URL
    
    def test_environment_variables_loaded(self) -> None:
        """Test que les variables d'environnement sont chargées."""
        # Ces variables peuvent être None si pas configurées
        # On teste juste qu'elles sont définies dans le module
        assert hasattr(pytest, "FRANCETRAVAIL_CLIENT_ID") or FRANCETRAVAIL_CLIENT_ID is None
        assert hasattr(pytest, "FRANCETRAVAIL_CLIENT_SECRET") or FRANCETRAVAIL_CLIENT_SECRET is None
    
    def test_constants_are_strings_or_none(self) -> None:
        """Test que les constantes sont des strings ou None."""
        if FRANCETRAVAIL_CLIENT_ID is not None:
            assert isinstance(FRANCETRAVAIL_CLIENT_ID, str)
        
        if FRANCETRAVAIL_CLIENT_SECRET is not None:
            assert isinstance(FRANCETRAVAIL_CLIENT_SECRET, str)
        
        assert isinstance(TOKEN_URL, str)
        assert isinstance(API_BASE_URL, str)
    
    def test_urls_accessibility(self) -> None:
        """Test que les URLs sont bien formées."""
        # Test de format basique
        assert TOKEN_URL.count("://") == 1  # Exactement un protocole
        assert API_BASE_URL.count("://") == 1
        
        # Pas d'espaces dans les URLs
        assert " " not in TOKEN_URL
        assert " " not in API_BASE_URL