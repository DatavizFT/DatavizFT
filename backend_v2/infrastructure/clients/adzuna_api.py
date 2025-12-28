"""
Client API Adzuna - Backend v2 (infrastructure)
Gestion de l'authentification, pagination, collecte d'offres
"""


import os
import time
from typing import Any, Dict, List, Optional
import httpx

from backend_v2.config import Config

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/fr/search/"

class AdzunaAPIClient:
    """Client API Adzuna (infrastructure)"""
    SOURCE = "Adzuna"

    def __init__(self, user_agent: str = "DatavizFT-Collector/1.0", rate_limit_ms: int = 120):
        from backend_v2.shared import logger
        self.user_agent = user_agent
        self.rate_limit_ms = rate_limit_ms
        self.base_url = ADZUNA_BASE_URL
        self.logger = logger.bind(client="AdzunaAPIClient")
        self.logger.info("Initialisation du client Adzuna API", user_agent=user_agent)

    def collect_offres_paginated(
        self,
        params: Dict[str, Any],
        page_size: int = 50,
        max_offres: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self.logger.info("Début de la collecte paginée des offres Adzuna", params=params, page_size=page_size, max_offres=max_offres)
        toutes_offres = []
        page = 1
        total_collected = 0
        while True:
            url = f"{self.base_url}{page}"
            query_params = {
                "app_id": Config.ADZUNA_APP_ID,
                "app_key": Config.ADZUNA_CLIENT_SECRET,
                "results_per_page": page_size,
                **params
            }
            headers = {"User-Agent": self.user_agent}
            response = httpx.get(url, params=query_params, headers=headers)
            if response.status_code != 200:
                self.logger.error("Erreur HTTP lors de la collecte d'une page Adzuna", status_code=response.status_code, page=page, response_text=response.text[:500])
                break
            data = response.json()
            if page == 1:
                self.logger.info("Réponse Adzuna page 1", count=data.get("count", 0), nb_results=len(data.get("results", [])))
            offres_page = data.get("results", [])
            toutes_offres.extend(offres_page)
            total_collected += len(offres_page)
            self.logger.info("Offres récupérées pour la page Adzuna", page=page, nb_offres=len(offres_page))
            if not offres_page or (max_offres and total_collected >= max_offres):
                break
            page += 1
            time.sleep(self.rate_limit_ms / 1000.0)
        self.logger.info("Collecte paginée Adzuna terminée", total_offres=len(toutes_offres))
        return toutes_offres
