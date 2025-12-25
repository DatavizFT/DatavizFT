#!/usr/bin/env python3
"""
Vérificateur rapide Docker pour DatavizFT
Execute après l'installation de Docker Desktop
"""

import subprocess
import sys


def check_docker_quick():
    """Vérification rapide de Docker"""
    print("Verification rapide de Docker Desktop...")
    print("=" * 40)

    # Test 1: Docker command
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"✅ Docker installe: {result.stdout.strip()}")
        else:
            print("❌ Docker non trouve")
            return False

    except FileNotFoundError:
        print("❌ Commande docker non trouvee")
        print("💡 Assurez-vous que Docker Desktop est installe et redemarrez le terminal")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Docker ne repond pas")
        return False

    # Test 2: Docker daemon
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            print("✅ Docker Engine fonctionne")
            return True
        else:
            print("❌ Docker Engine arrete")
            print("💡 Lancez Docker Desktop et attendez que l'icone soit verte")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker Engine ne repond pas")
        print("💡 Verifiez que Docker Desktop est demarre")
        return False


def main():
    """Test principal"""
    if check_docker_quick():
        print("\n🎉 Docker Desktop est pret!")
        print("🚀 Vous pouvez maintenant lancer:")
        print("   python scripts/setup_docker_persistence.py")
        return True
    else:
        print("\n⚠️  Docker Desktop pas encore pret")
        print("📋 Actions a faire:")
        print("   1. Installer Docker Desktop si pas fait")
        print("   2. Redemarrer l'ordinateur si demande")
        print("   3. Lancer Docker Desktop")
        print("   4. Attendre que l'icone soit verte")
        print("   5. Relancer ce script")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
