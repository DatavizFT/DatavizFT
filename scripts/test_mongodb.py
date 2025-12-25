#!/usr/bin/env python3
"""
Test de connexion MongoDB pour DatavizFT
Vérifie la connexion, les collections et effectue des tests basiques
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le backend au path Python
sys.path.append(str(Path(__file__).parent.parent))

try:
    import dns.resolver  # Pour les connexions SRV
    import pymongo
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    print("📦 Installez les dépendances: pip install pymongo motor dnspython")
    sys.exit(1)

from backend.config import Config


class MongoDBTester:
    """Testeur de connexion MongoDB"""

    def __init__(self):
        """Initialise le testeur"""
        self.config = Config()
        self.mongodb_url = self.config.MONGODB_URL
        self.database_name = self.config.MONGODB_DATABASE

        # Clients (à initialiser)
        self.sync_client: MongoClient | None = None
        self.async_client: AsyncIOMotorClient | None = None

    def test_sync_connection(self) -> bool:
        """Test de connexion synchrone"""
        print("🔍 Test de connexion synchrone...")

        try:
            # Créer le client MongoDB
            self.sync_client = MongoClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 secondes
                connectTimeoutMS=5000,
            )

            # Test de connexion
            server_info = self.sync_client.server_info()
            print("✅ Connexion synchrone réussie!")
            print(f"   Version MongoDB: {server_info.get('version')}")
            print(f"   URL: {self.mongodb_url}")

            # Tester l'accès à la base
            db = self.sync_client[self.database_name]
            collections = db.list_collection_names()
            print(f"   Base de données: {self.database_name}")
            print(f"   Collections: {len(collections)} ({', '.join(collections)})")

            return True

        except pymongo.errors.ServerSelectionTimeoutError:
            print("❌ Impossible de se connecter au serveur MongoDB")
            print("   Vérifiez que MongoDB est démarré")
            print("   URL testée:", self.mongodb_url)
            return False
        except pymongo.errors.AuthenticationFailed:
            print("❌ Authentification échouée")
            print("   Vérifiez les identifiants dans .env")
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

    async def test_async_connection(self) -> bool:
        """Test de connexion asynchrone"""
        print("\n🔍 Test de connexion asynchrone...")

        try:
            # Créer le client async
            self.async_client = AsyncIOMotorClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000,
            )

            # Test de connexion
            server_info = await self.async_client.server_info()
            print("✅ Connexion asynchrone réussie!")
            print(f"   Version MongoDB: {server_info.get('version')}")

            # Test d'accès à la base
            db = self.async_client[self.database_name]
            collections = await db.list_collection_names()
            print(f"   Collections: {len(collections)} ({', '.join(collections)})")

            return True

        except Exception as e:
            print(f"❌ Erreur de connexion async: {e}")
            return False

    async def test_crud_operations(self) -> bool:
        """Test des opérations CRUD basiques"""
        print("\n🧪 Test des opérations CRUD...")

        try:
            db = self.async_client[self.database_name]
            test_collection = db.test_datavizft

            # CREATE: Insérer un document test
            test_doc = {
                "test_id": "mongodb_test_001",
                "message": "Test DatavizFT MongoDB",
                "timestamp": datetime.now(),
                "data": {"framework": "FastAPI", "database": "MongoDB"},
            }

            insert_result = await test_collection.insert_one(test_doc)
            print(f"✅ Insertion réussie: {insert_result.inserted_id}")

            # READ: Lire le document
            found_doc = await test_collection.find_one({"test_id": "mongodb_test_001"})
            if found_doc:
                print(f"✅ Lecture réussie: {found_doc['message']}")
            else:
                print("❌ Document non trouvé")
                return False

            # UPDATE: Modifier le document
            update_result = await test_collection.update_one(
                {"test_id": "mongodb_test_001"}, {"$set": {"status": "updated"}}
            )
            print(f"✅ Mise à jour réussie: {update_result.modified_count} document(s)")

            # DELETE: Supprimer le document
            delete_result = await test_collection.delete_one({"test_id": "mongodb_test_001"})
            print(f"✅ Suppression réussie: {delete_result.deleted_count} document(s)")

            return True

        except Exception as e:
            print(f"❌ Erreur CRUD: {e}")
            return False

    async def test_collections_schema(self) -> bool:
        """Test de la structure des collections DatavizFT"""
        print("\n📋 Vérification des collections DatavizFT...")

        try:
            db = self.async_client[self.database_name]

            # Collections attendues
            expected_collections = [
                "offres",
                "competences",
                "competences_detections",
                "stats_competences",
            ]

            existing_collections = await db.list_collection_names()

            # Vérifier les collections
            for collection_name in expected_collections:
                if collection_name in existing_collections:
                    collection = db[collection_name]
                    count = await collection.count_documents({})
                    print(f"✅ {collection_name}: {count} documents")

                    # Vérifier les index
                    indexes = await collection.index_information()
                    print(f"   Index: {len(indexes)} ({', '.join(indexes.keys())})")
                else:
                    print(f"⚠️  Collection manquante: {collection_name}")

            return True

        except Exception as e:
            print(f"❌ Erreur de vérification des collections: {e}")
            return False

    async def test_aggregation(self) -> bool:
        """Test des opérations d'agrégation"""
        print("\n📊 Test des agrégations MongoDB...")

        try:
            db = self.async_client[self.database_name]
            test_collection = db.test_aggregation

            # Insérer des données de test
            test_data = [
                {"competence": "Python", "niveau": "expert", "salaire": 50000},
                {"competence": "JavaScript", "niveau": "confirme", "salaire": 45000},
                {"competence": "Python", "niveau": "confirme", "salaire": 40000},
                {"competence": "MongoDB", "niveau": "debutant", "salaire": 35000},
            ]

            await test_collection.insert_many(test_data)
            print(f"✅ {len(test_data)} documents de test insérés")

            # Agrégation: moyenne de salaire par compétence
            pipeline = [
                {"$group": {"_id": "$competence", "salaire_moyen": {"$avg": "$salaire"}, "nb_offres": {"$sum": 1}}},
                {"$sort": {"salaire_moyen": -1}},
            ]

            cursor = test_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            print("📊 Résultats d'agrégation:")
            for result in results:
                print(f"   {result['_id']}: {result['salaire_moyen']:,.0f}€ ({result['nb_offres']} offres)")

            # Nettoyer les données de test
            await test_collection.drop()
            print("🗑️  Données de test nettoyées")

            return True

        except Exception as e:
            print(f"❌ Erreur d'agrégation: {e}")
            return False

    def close_connections(self):
        """Fermer les connexions"""
        if self.sync_client:
            self.sync_client.close()
            print("🔌 Connexion synchrone fermée")

        if self.async_client:
            self.async_client.close()
            print("🔌 Connexion asynchrone fermée")


async def main():
    """Fonction principale de test"""
    print("🧪 Test de connexion MongoDB - DatavizFT")
    print("=" * 50)

    # Vérifier les variables d'environnement
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("❌ Variable MONGODB_URL manquante dans .env")
        print("💡 Ajoutez: MONGODB_URL=mongodb://admin:password@localhost:27017/dataviz_ft_dev?authSource=admin")
        return False

    # Initialiser le testeur
    tester = MongoDBTester()

    try:
        # Tests de connexion
        sync_ok = tester.test_sync_connection()
        if not sync_ok:
            return False

        async_ok = await tester.test_async_connection()
        if not async_ok:
            return False

        # Tests fonctionnels
        crud_ok = await tester.test_crud_operations()
        schema_ok = await tester.test_collections_schema()
        aggregation_ok = await tester.test_aggregation()

        # Résumé final
        print("\n" + "=" * 50)
        if all([sync_ok, async_ok, crud_ok, schema_ok, aggregation_ok]):
            print("🎉 Tous les tests MongoDB réussis!")
            print("✅ DatavizFT est prêt à utiliser MongoDB")
            return True
        else:
            print("⚠️  Certains tests ont échoué")
            return False

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

    finally:
        tester.close_connections()


if __name__ == "__main__":
    # Charger les variables d'environnement
    from dotenv import load_dotenv

    load_dotenv()

    # Lancer les tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
