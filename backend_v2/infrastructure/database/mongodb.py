"""
MongoDB Connection - Gestion centralisée de la connexion MongoDB pour l'infrastructure backend_v2
Utilise motor (async) et pymongo (sync) selon les besoins
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from backend_v2.shared import logger

class MongoDBConnection:
    """Gestionnaire de connexion MongoDB pour backend_v2"""
    def __init__(self, connection_string: str | None = None):
        """
        Initialise la connexion MongoDB
        Args:
            connection_string: URI MongoDB (défaut: variable d'env MONGODB_URL)
        """
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URL", "mongodb://localhost:27017"
        )
        self.database_name = os.getenv("MONGODB_DATABASE", "dataviz_ft")
        self._async_client: AsyncIOMotorClient | None = None
        self._sync_client: MongoClient | None = None
        self._async_db: AsyncIOMotorDatabase | None = None
        self._sync_db: Database | None = None
        logger.info(f"[MongoDB] Initialisation avec URI: {self.connection_string}, DB: {self.database_name}")


    @property
    def async_client(self) -> AsyncIOMotorClient:
        """Client MongoDB asynchrone (Motor)"""
        if self._async_client is None:
            try:
                self._async_client = AsyncIOMotorClient(self.connection_string)
                # Tentative de ping pour vérifier la connexion
                # (nécessite un event loop, donc à faire côté appelant si besoin)
                logger.info("[MongoDB] Client asynchrone initialisé.")
            except Exception as e:
                logger.error(f"[MongoDB] Erreur d'initialisation du client asynchrone: {e}")
                raise
        return self._async_client

    @property
    def async_db(self) -> AsyncIOMotorDatabase:
        """Base MongoDB asynchrone (Motor)"""
        if self._async_db is None:
            self._async_db = self.async_client[self.database_name]
        return self._async_db

    @property
    def sync_client(self) -> MongoClient:
        """Client MongoDB synchrone (PyMongo)"""
        if self._sync_client is None:
            self._sync_client = MongoClient(self.connection_string)
        return self._sync_client

    @property
    def sync_db(self) -> Database:
        """Base MongoDB synchrone (PyMongo)"""
        if self._sync_db is None:
            self._sync_db = self.sync_client[self.database_name]
        return self._sync_db
