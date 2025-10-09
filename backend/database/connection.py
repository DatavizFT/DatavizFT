"""
Database Connection - Gestion des connexions MongoDB
Centralise la configuration et l'initialisation de MongoDB
"""

import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database


class DatabaseConnection:
    """Gestionnaire de connexion MongoDB"""

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

        # Clients (initialisés à None)
        self._async_client: AsyncIOMotorClient | None = None
        self._sync_client: MongoClient | None = None
        self._async_db: AsyncIOMotorDatabase | None = None
        self._sync_db: Database | None = None

    @property
    def async_client(self) -> AsyncIOMotorClient:
        """Client MongoDB asynchrone (Motor)"""
        if self._async_client is None:
            self._async_client = AsyncIOMotorClient(self.connection_string)
        return self._async_client

    @property
    def sync_client(self) -> MongoClient:
        """Client MongoDB synchrone (PyMongo)"""
        if self._sync_client is None:
            self._sync_client = MongoClient(self.connection_string)
        return self._sync_client

    @property
    def async_db(self) -> AsyncIOMotorDatabase:
        """Base de données asynchrone"""
        if self._async_db is None:
            self._async_db = self.async_client[self.database_name]
        return self._async_db

    @property
    def sync_db(self) -> Database:
        """Base de données synchrone"""
        if self._sync_db is None:
            self._sync_db = self.sync_client[self.database_name]
        return self._sync_db

    async def connect(self) -> bool:
        """
        Teste la connexion à MongoDB

        Returns:
            True si connexion réussie, False sinon
        """
        try:
            # Test ping asynchrone
            await self.async_client.admin.command("ping")
            print(f"✅ Connexion MongoDB réussie: {self.database_name}")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion MongoDB: {e}")
            return False

    def connect_sync(self) -> bool:
        """
        Teste la connexion MongoDB synchrone

        Returns:
            True si connexion réussie, False sinon
        """
        try:
            # Test ping synchrone
            self.sync_client.admin.command("ping")
            print(f"✅ Connexion MongoDB synchrone réussie: {self.database_name}")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion MongoDB synchrone: {e}")
            return False

    async def close(self):
        """Ferme les connexions MongoDB"""
        if self._async_client:
            self._async_client.close()
            self._async_client = None
            self._async_db = None

        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
            self._sync_db = None

        print("🔌 Connexions MongoDB fermées")

    async def create_indexes(self):
        """Crée les index optimaux pour les collections"""
        db = self.async_db

        # Index pour collection offres
        await db.offres.create_index(
            [("source_id", 1)], unique=True, name="idx_source_id"  # Unique ID source
        )

        await db.offres.create_index(
            [("date_creation", -1)],  # Tri par date création desc
            name="idx_date_creation",
        )

        await db.offres.create_index(
            [("competences_extraites", 1)],  # Recherche par compétences
            name="idx_competences",
        )

        await db.offres.create_index(
            [
                ("localisation.departement", 1),  # Recherche géographique
                ("date_creation", -1),
            ],
            name="idx_geo_date",
        )

        # Index géospatial si coordonnées présentes
        await db.offres.create_index(
            [("localisation.coordinates", "2dsphere")],
            name="idx_geo_coords",
            sparse=True,
        )

        # Index pour collection stats_competences
        await db.stats_competences.create_index(
            [("competence", 1), ("periode", 1)],
            unique=True,
            name="idx_competence_periode",
        )

        await db.stats_competences.create_index(
            [("date_analyse", -1)], name="idx_date_analyse"
        )

        print("📊 Index MongoDB créés avec succès")

    def get_collection_info(self) -> dict:
        """Obtient des informations sur les collections"""
        try:
            db = self.sync_db
            collections = db.list_collection_names()

            info = {"database": self.database_name, "collections": {}}

            for coll_name in collections:
                coll = db[coll_name]
                info["collections"][coll_name] = {
                    "count": coll.count_documents({}),
                    "indexes": len(list(coll.list_indexes())),
                    "size_mb": round(
                        coll.estimated_document_count() * 0.001, 2
                    ),  # Estimation
                }

            return info

        except Exception as e:
            return {"error": str(e)}


# Instance globale de connexion
_db_connection: DatabaseConnection | None = None


def get_database_connection() -> DatabaseConnection:
    """Récupère l'instance globale de connexion"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def get_database() -> AsyncIOMotorDatabase:
    """Récupère la base de données asynchrone"""
    return get_database_connection().async_db


def get_sync_database() -> Database:
    """Récupère la base de données synchrone"""
    return get_database_connection().sync_db


async def init_database() -> bool:
    """
    Initialise la connexion et crée les index

    Returns:
        True si initialisation réussie
    """
    conn = get_database_connection()

    # Test de connexion
    if not await conn.connect():
        return False

    # Création des index
    try:
        await conn.create_indexes()
        return True
    except Exception as e:
        print(f"❌ Erreur création index: {e}")
        return False


async def close_database():
    """Ferme la connexion globale"""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None


# Configuration pour différents environnements
DATABASE_CONFIGS = {
    "development": {"url": "mongodb://localhost:27017", "database": "dataviz_ft_dev"},
    "test": {"url": "mongodb://localhost:27017", "database": "dataviz_ft_test"},
    "production": {
        "url": os.getenv("MONGODB_URL_PROD", "mongodb://localhost:27017"),
        "database": "dataviz_ft_prod",
    },
}


def get_config(env: str = "development") -> dict:
    """Récupère la config pour un environnement"""
    return DATABASE_CONFIGS.get(env, DATABASE_CONFIGS["development"])
