#!/usr/bin/env python3
"""
Test de connectivité vers l'API France Travail
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import httpx

from backend.config import (
    FRANCETRAVAIL_CLIENT_ID,
    FRANCETRAVAIL_CLIENT_SECRET,
    TOKEN_URL,
)


def test_connectivity():
    """Test de base de la connectivité"""

    print("🔍 Test de connectivité API France Travail...")
    print(f"Token URL: {TOKEN_URL}")
    print(f"Client ID configuré: {bool(FRANCETRAVAIL_CLIENT_ID)}")
    print(f"Client Secret configuré: {bool(FRANCETRAVAIL_CLIENT_SECRET)}")

    if not FRANCETRAVAIL_CLIENT_ID or not FRANCETRAVAIL_CLIENT_SECRET:
        print("❌ Credentials manquants dans .env")
        return False

    try:
        # Test simple de résolution DNS et connectivité
        print("\n🌐 Test de connectivité...")

        response = httpx.get("https://www.francetravail.fr", timeout=10.0)
        print(f"✅ Connectivité OK - Status: {response.status_code}")

        # Test d'authentification
        print("\n🔑 Test d'authentification...")

        response = httpx.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": FRANCETRAVAIL_CLIENT_ID,
                "client_secret": FRANCETRAVAIL_CLIENT_SECRET,
                "scope": "api_offresdemploiv2 o2dsoffre",
            },
            timeout=10.0
        )

        print(f"Auth response status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Authentification réussie")
            token_data = response.json()
            print(f"Token type: {token_data.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur connectivité: {e}")
        return False

if __name__ == "__main__":
    test_connectivity()
