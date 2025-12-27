"""
Script de test direct du CollectionService
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_v2.application.services import CollectionService


async def main():
    print("=" * 80)
    print("TEST DIRECT COLLECTION SERVICE")
    print("=" * 80)

    service = CollectionService()

    print("\nTest collecte France Travail uniquement...\n")

    result_ft = await service._collect_france_travail(max_offres=10)

    print(f"\nRésultat France Travail:")
    print(f"  Nouvelles offres: {result_ft.get('nouvelles_offres', 0)}")
    print(f"  Doublons: {result_ft.get('doublons', 0)}")
    print(f"  Total collectées: {result_ft.get('total_collectees', 0)}")

    if "error" in result_ft:
        print(f"  ERREUR: {result_ft['error']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
