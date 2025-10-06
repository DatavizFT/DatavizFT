"""
API Client - Client générique pour les APIs de France Travail
Gestion de l'authentification, pagination, rate limiting
"""

import time
from typing import Any

import httpx

from ..config import (
    API_BASE_URL,
    FRANCETRAVAIL_CLIENT_ID,
    FRANCETRAVAIL_CLIENT_SECRET,
    TOKEN_URL,
)


class FranceTravailAPIClient:
    """Client API générique pour France Travail"""

    def __init__(
        self, user_agent: str = "DatavizFT-Collector/1.0", rate_limit_ms: int = 120
    ):
        self.user_agent = user_agent
        self.rate_limit_ms = rate_limit_ms
        self.base_url = API_BASE_URL
        self._headers = None
        self._token = None

    def _get_token(self):
        """Obtient un token d'authentification OAuth2 pour l'API France Travail"""
        if self._token is not None:
            return self._token

        print("Requesting new token...")

        # Vérification des credentials
        if not FRANCETRAVAIL_CLIENT_ID or not FRANCETRAVAIL_CLIENT_SECRET:
            raise ValueError(
                "Client ID and Client Secret must be configured in .env file"
            )

        try:
            response = httpx.post(
                TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": FRANCETRAVAIL_CLIENT_ID,
                    "client_secret": FRANCETRAVAIL_CLIENT_SECRET,
                    "scope": "api_offresdemploiv2 o2dsoffre",
                },
            )

            print(f"Auth response status: {response.status_code}")

            if response.status_code == 400:
                error_details = (
                    response.json() if response.text else {"error": "Unknown error"}
                )
                print(f"Authentication failed: {error_details}")
                raise ValueError(
                    f"Authentication failed: {error_details.get('error_description', 'Invalid credentials')}"
                )

            response.raise_for_status()
            token_data = response.json()
            print("Token received successfully")
            self._token = token_data["access_token"]
            return self._token

        except httpx.HTTPStatusError as e:
            print(f"HTTP error during authentication: {e}")
            print(f"Response content: {e.response.text}")
            raise ValueError(
                f"Failed to authenticate with France Travail API: {e.response.status_code}"
            ) from e
        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            raise ValueError(f"Authentication error: {str(e)}") from e

    def _get_headers(self) -> dict[str, str]:
        """Obtient les headers avec token d'authentification"""
        if not self._headers:
            token = self._get_token()
            self._headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            }
        return self._headers

    def _parse_content_range(self, content_range: str) -> int:
        """
        Parse l'header Content-Range pour obtenir le total d'éléments

        Args:
            content_range: Header Content-Range (ex: "items 0-149/663")

        Returns:
            Nombre total d'éléments disponibles
        """
        if not content_range:
            raise ValueError("Header Content-Range manquant")

        try:
            return int(content_range.split("/")[-1])
        except (IndexError, ValueError):
            raise ValueError(
                f"Format Content-Range invalide: {content_range}"
            ) from None

    def obtenir_total_offres(self, params: dict[str, Any]) -> int:
        """
        Obtient le nombre total d'offres pour une requête donnée

        Args:
            params: Paramètres de la requête

        Returns:
            Nombre total d'offres disponibles
        """
        url = f"{self.base_url}/offres/search"
        headers = self._get_headers()

        # Requête avec range minimal pour obtenir le total
        response = httpx.get(url, headers=headers, params={**params, "range": "0-0"})

        if response.status_code not in [200, 206]:
            raise Exception(f"Erreur API: {response.status_code} - {response.text}")

        content_range = response.headers.get("Content-Range", "")
        return self._parse_content_range(content_range)

    def collecter_offres_paginees(
        self,
        params: dict[str, Any],
        page_size: int = 150,
        max_offres: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Collecte les offres avec pagination automatique

        Args:
            params: Paramètres de base de la requête
            page_size: Taille de page (max 150)
            max_offres: Limite optionnelle du nombre d'offres à collecter

        Returns:
            Liste complète des offres collectées
        """
        print("🚀 DÉBUT COLLECTE AVEC PAGINATION")
        print("=" * 50)

        # Obtenir le total disponible
        total_disponible = self.obtenir_total_offres(params)
        total_a_collecter = min(total_disponible, max_offres or total_disponible)

        print(f"📊 {total_disponible} offres disponibles")
        if max_offres:
            print(f"🎯 Limite fixée à {max_offres} offres")
        print(f"📥 Collecte de {total_a_collecter} offres")

        # Configuration pagination
        page_size = min(page_size, 150)  # Limite API
        nb_pages = (total_a_collecter + page_size - 1) // page_size

        print(f"📄 Collecte en {nb_pages} pages de {page_size} offres max")

        # Collecte paginée
        toutes_offres = []
        url = f"{self.base_url}/offres/search"
        headers = self._get_headers()

        for page in range(nb_pages):
            start = page * page_size
            end = min(start + page_size - 1, total_a_collecter - 1)
            range_param = f"{start}-{end}"

            print(f"   📄 Page {page + 1}/{nb_pages}: range={range_param}")

            params_page = {**params, "range": range_param}
            response = httpx.get(url, headers=headers, params=params_page)

            if response.status_code in [200, 206]:
                data = response.json()
                offres_page = data.get("resultats", [])
                toutes_offres.extend(offres_page)
                print(
                    f"   ✅ {len(offres_page)} offres collectées (total: {len(toutes_offres)})"
                )

                # Arrêt si limite atteinte
                if len(toutes_offres) >= total_a_collecter:
                    break
            else:
                print(f"   ❌ Erreur page {page + 1}: {response.status_code}")
                # Continuer malgré l'erreur pour les autres pages

            # Rate limiting
            time.sleep(self.rate_limit_ms / 1000.0)

        print(f"\n🎯 COLLECTE TERMINÉE: {len(toutes_offres)} offres")
        return toutes_offres

    def collecter_offres_par_code_rome(
        self, code_rome: str, **kwargs
    ) -> list[dict[str, Any]]:
        """
        Collecte les offres pour un code ROME spécifique

        Args:
            code_rome: Code ROME à rechercher (ex: "M1805")
            **kwargs: Arguments additionnels pour collecter_offres_paginees

        Returns:
            Liste des offres pour ce code ROME
        """
        params_base = {"codeROME": code_rome}
        return self.collecter_offres_paginees(params_base, **kwargs)

    def collecter_offres_avec_filtres(
        self, filtres: dict[str, Any], **kwargs
    ) -> list[dict[str, Any]]:
        """
        Collecte les offres avec des filtres personnalisés

        Args:
            filtres: Dictionnaire des filtres API
            **kwargs: Arguments additionnels pour collecter_offres_paginees

        Returns:
            Liste des offres correspondant aux filtres
        """
        return self.collecter_offres_paginees(filtres, **kwargs)


# Fonction utilitaire pour compatibilité
def collecter_toutes_offres_m1805() -> list[dict[str, Any]]:
    """
    Fonction de compatibilité pour collecter toutes les offres M1805

    Returns:
        Liste complète des offres M1805
    """
    client = FranceTravailAPIClient()
    return client.collecter_offres_par_code_rome("M1805")
