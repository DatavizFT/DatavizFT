#!/usr/bin/env python3
"""
Configuration et test de persistance MongoDB Docker
Vérifie Docker, configure les volumes et teste la persistance
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class DockerMongoDBSetup:
    """Configuration Docker MongoDB avec persistance"""

    def __init__(self):
        """Initialise la configuration"""
        self.project_root = Path(__file__).parent.parent
        self.compose_file = self.project_root / "docker-compose.yml"

    def check_docker(self) -> bool:
        """Vérifie si Docker est installé et fonctionne"""
        print("🐳 Vérification de Docker...")

        try:
            # Test Docker version
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"✅ Docker installé: {result.stdout.strip()}")
            else:
                print("❌ Docker non installé")
                return False

            # Test Docker daemon
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("✅ Docker Engine fonctionne")
                return True
            else:
                print("❌ Docker Engine arrêté")
                print("💡 Lancez Docker Desktop puis relancez ce script")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Docker ne répond pas (timeout)")
            return False
        except FileNotFoundError:
            print("❌ Docker non trouvé dans PATH")
            return False
        except Exception as e:
            print(f"❌ Erreur Docker: {e}")
            return False

    def check_compose_file(self) -> bool:
        """Vérifie le fichier docker-compose.yml"""
        print(f"📋 Vérification de {self.compose_file}...")

        if not self.compose_file.exists():
            print("❌ Fichier docker-compose.yml manquant")
            return False

        print("✅ Fichier docker-compose.yml trouvé")

        # Vérifier la configuration des volumes
        try:
            content = self.compose_file.read_text(encoding="utf-8")

            if "mongodb_data:/data/db" in content:
                print("✅ Volume persistant configuré")
            else:
                print("⚠️  Configuration de volume à vérifier")

            if "volumes:" in content and "mongodb_data:" in content:
                print("✅ Volume nommé défini")
            else:
                print("⚠️  Volume nommé manquant")

            return True

        except Exception as e:
            print(f"❌ Erreur lecture docker-compose.yml: {e}")
            return False

    def start_mongodb(self) -> bool:
        """Démarre MongoDB avec Docker Compose"""
        print("🚀 Démarrage de MongoDB avec persistance...")

        try:
            # Naviguer vers le dossier du projet
            os.chdir(self.project_root)

            # Démarrer les services
            result = subprocess.run(
                ["docker", "compose", "up", "-d", "mongodb", "mongo-express"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes max
            )

            if result.returncode == 0:
                print("✅ MongoDB démarré avec succès!")
                print(result.stdout)
                return True
            else:
                print("❌ Erreur au démarrage de MongoDB:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Timeout au démarrage de MongoDB")
            return False
        except Exception as e:
            print(f"❌ Erreur démarrage: {e}")
            return False

    def check_containers(self) -> bool:
        """Vérifie l'état des conteneurs"""
        print("🔍 Vérification des conteneurs...")

        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')

                mongodb_running = False
                mongo_express_running = False

                for line in lines:
                    if "datavizft_mongodb" in line:
                        print(f"🗄️  MongoDB: {line}")
                        mongodb_running = "Up" in line
                    elif "datavizft_mongo_express" in line:
                        print(f"🌐 Mongo Express: {line}")
                        mongo_express_running = "Up" in line

                if mongodb_running:
                    print("✅ MongoDB fonctionne")
                else:
                    print("❌ MongoDB arrêté")

                if mongo_express_running:
                    print("✅ Mongo Express fonctionne")
                    print("🌐 Interface: http://localhost:8081")
                    print("🔑 Login: datavizft / admin123")
                else:
                    print("⚠️  Mongo Express non disponible")

                return mongodb_running

        except Exception as e:
            print(f"❌ Erreur vérification conteneurs: {e}")
            return False

    def check_volumes(self) -> bool:
        """Vérifie les volumes Docker persistants"""
        print("💾 Vérification des volumes persistants...")

        try:
            result = subprocess.run(
                ["docker", "volume", "ls", "--format", "table {{.Name}}\\t{{.Driver}}\\t{{.Mountpoint}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                if "datavizft_mongodb_data" in result.stdout:
                    print("✅ Volume MongoDB persistant créé")

                    # Obtenir les détails du volume
                    volume_result = subprocess.run(
                        ["docker", "volume", "inspect", "datavizft_mongodb_data"],
                        capture_output=True,
                        text=True
                    )

                    if volume_result.returncode == 0:
                        import json
                        volume_info = json.loads(volume_result.stdout)[0]
                        mountpoint = volume_info.get("Mountpoint", "N/A")
                        print(f"📂 Emplacement: {mountpoint}")

                    return True
                else:
                    print("❌ Volume MongoDB manquant")
                    return False

        except Exception as e:
            print(f"❌ Erreur vérification volumes: {e}")
            return False

    def test_persistence(self) -> bool:
        """Test de persistance des données"""
        print("🧪 Test de persistance des données...")

        try:
            # Attendre que MongoDB soit prêt
            print("⏳ Attente de MongoDB (30s max)...")

            for i in range(30):
                try:
                    result = subprocess.run(
                        ["docker", "exec", "datavizft_mongodb", "mongosh",
                         "--eval", "db.version()", "--quiet"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0:
                        print("✅ MongoDB prêt")
                        break
                except:
                    pass

                time.sleep(1)
                print(f"   Tentative {i+1}/30...")
            else:
                print("❌ MongoDB pas prêt après 30s")
                return False

            # Insérer un document de test
            test_command = '''
            db = db.getSiblingDB('dataviz_ft_dev');
            db.test_persistence.insertOne({
                test: 'persistence_test',
                timestamp: new Date(),
                message: 'Test de persistance DatavizFT'
            });
            db.test_persistence.findOne({test: 'persistence_test'});
            '''

            result = subprocess.run(
                ["docker", "exec", "datavizft_mongodb", "mongosh",
                 "dataviz_ft_dev", "--eval", test_command, "--quiet"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and "persistence_test" in result.stdout:
                print("✅ Données insérées avec succès")
                print("💾 Test de persistance : données stockées dans le volume")
                return True
            else:
                print("❌ Échec insertion des données de test")
                print(f"Sortie: {result.stdout}")
                print(f"Erreur: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Erreur test persistance: {e}")
            return False

    def show_connection_info(self):
        """Affiche les informations de connexion"""
        print("\n" + "="*60)
        print("🎉 Configuration Docker MongoDB terminée!")
        print("="*60)

        print("\n📊 Informations de connexion:")
        print("   URL MongoDB: mongodb://admin:datavizft2025@localhost:27017/dataviz_ft_dev?authSource=admin")
        print("   Base de données: dataviz_ft_dev")
        print("   Admin: admin / datavizft2025")

        print("\n🌐 Interface Web Mongo Express:")
        print("   URL: http://localhost:8081")
        print("   Login: datavizft / admin123")

        print("\n💾 Persistance:")
        print("   ✅ Volume Docker: datavizft_mongodb_data")
        print("   ✅ Données persistantes même après redémarrage")

        print("\n🛠️  Commandes utiles:")
        print("   Arrêter:    docker compose down")
        print("   Redémarrer: docker compose up -d mongodb mongo-express")
        print("   Logs:       docker compose logs mongodb")
        print("   Shell:      docker exec -it datavizft_mongodb mongosh")

        print("\n🧪 Test de connexion Python:")
        print("   python scripts/test_mongodb.py")


def main():
    """Fonction principale"""
    print("🐳 Configuration Docker MongoDB avec Persistance")
    print("=" * 55)

    setup = DockerMongoDBSetup()

    # Étapes de configuration
    steps = [
        ("Vérification Docker", setup.check_docker),
        ("Vérification docker-compose.yml", setup.check_compose_file),
        ("Démarrage MongoDB", setup.start_mongodb),
        ("Vérification conteneurs", setup.check_containers),
        ("Vérification volumes", setup.check_volumes),
        ("Test persistance", setup.test_persistence),
    ]

    success_count = 0

    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} réussi")
            else:
                print(f"❌ {step_name} échoué")
                if step_name == "Vérification Docker":
                    print("\n💡 Solutions:")
                    print("   1. Attendez que Docker Desktop termine l'installation")
                    print("   2. Redémarrez votre ordinateur")
                    print("   3. Lancez Docker Desktop manuellement")
                    print("   4. Relancez ce script")
                    break
        except Exception as e:
            print(f"❌ Erreur {step_name}: {e}")

    # Résumé final
    print(f"\n📊 Résumé: {success_count}/{len(steps)} étapes réussies")

    if success_count == len(steps):
        setup.show_connection_info()
        return True
    else:
        print("\n⚠️  Configuration incomplète. Vérifiez les erreurs ci-dessus.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
