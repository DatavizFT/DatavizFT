"""
Client API France Travail - Backend v2 (infrastructure)
Gestion de l'authentification, pagination, collecte d'offres
"""

import time
from typing import Any, Dict, List, Optional
import httpx
from backend_v2.config import (
    API_BASE_URL,
    FRANCETRAVAIL_CLIENT_ID,
    FRANCETRAVAIL_CLIENT_SECRET,
    TOKEN_URL,
)

class FranceTravailAPIClient:
    """Client API France Travail (infrastructure)"""
    def __init__(self, user_agent: str = "DatavizFT-Collector/1.0", rate_limit_ms: int = 120):
        self.user_agent = user_agent
        self.rate_limit_ms = rate_limit_ms
        self.base_url = API_BASE_URL
        self._token: Optional[str] = None
        self._headers: Optional[Dict[str, str]] = None

    def _get_token(self) -> str:
        if self._token is not None:
            return self._token
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
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def _get_headers(self) -> Dict[str, str]:
        if not self._headers:
            token = self._get_token()
            self._headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            }
        return self._headers

    def _parse_content_range(self, content_range: str) -> int:
        if not content_range:
            raise ValueError("Header Content-Range manquant")
        return int(content_range.split("/")[-1])

    def get_total_offres(self, params: Dict[str, Any]) -> int:
        url = f"{self.base_url}/offres/search"
        headers = self._get_headers()
        response = httpx.get(url, headers=headers, params={**params, "range": "0-0"})
        response.raise_for_status()
        content_range = response.headers.get("Content-Range", "")
        return self._parse_content_range(content_range)

    def collect_offres_paginated(
        self,
        params: Dict[str, Any],
        page_size: int = 150,
        max_offres: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        total_disponible = self.get_total_offres(params)
        total_a_collecter = min(total_disponible, max_offres or total_disponible)
        page_size = min(page_size, 150)
        nb_pages = (total_a_collecter + page_size - 1) // page_size
        toutes_offres = []
        url = f"{self.base_url}/offres/search"
        headers = self._get_headers()
        for page in range(nb_pages):
            start = page * page_size
            end = min(start + page_size - 1, total_a_collecter - 1)
            range_param = f"{start}-{end}"
            params_page = {**params, "range": range_param}
            response = httpx.get(url, headers=headers, params=params_page)
            if response.status_code in [200, 206]:
                data = response.json()
                offres_page = data.get("resultats", [])
                toutes_offres.extend(offres_page)
                if len(toutes_offres) >= total_a_collecter:
                    break
            time.sleep(self.rate_limit_ms / 1000.0)
        return toutes_offres

    def collect_offres_by_rome(self, code_rome: str, **kwargs) -> List[Dict[str, Any]]:
        params_base = {"codeROME": code_rome}
        return self.collect_offres_paginated(params_base, **kwargs)

    def collect_offres_with_filters(self, filtres: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        return self.collect_offres_paginated(filtres, **kwargs)

    def reset(self):
        self._token = None
        self._headers = None
