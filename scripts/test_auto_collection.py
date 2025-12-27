"""
Script de test pour la collecte automatisée
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_v2.application.services import CollectionService


async def main():
    """Tester la collecte automatisée"""
    print("=" * 80)
    print("TEST COLLECTE AUTOMATISEE - DatavizFT")
    print("=" * 80)

    service = CollectionService()

    print("\nLancement de la collecte multi-sources...")
    print("(France Travail + Adzuna + Extraction competences)\n")

    results = await service.collect_all_sources(max_offres_per_source=100)

    print("\n" + "=" * 80)
    print("RESULTATS")
    print("=" * 80)

    if results["success"]:
        print(f"\nTotal nouvelles offres: {results['total_nouvelles_offres']}")
        print(f"Total doublons: {results['total_doublons']}\n")

        print("Par source:")
        for source_name, source_data in results["sources"].items():
            if "error" in source_data:
                print(f"  {source_name}: ERREUR - {source_data['error']}")
            else:
                print(f"  {source_name}:")
                print(f"    - Nouvelles: {source_data.get('nouvelles_offres', 0)}")
                print(f"    - Doublons: {source_data.get('doublons', 0)}")
                print(f"    - Total collectees: {source_data.get('total_collectees', 0)}")

        if "extraction_competences" in results:
            ext = results["extraction_competences"]
            if "error" in ext:
                print(f"\nExtraction competences: ERREUR - {ext['error']}")
            else:
                print(f"\nExtraction competences:")
                print(f"  - Offres analysees: {ext.get('offres_analysees', 0)}")
                print(f"  - Offres avec competences: {ext.get('offres_avec_competences', 0)}")
                print(f"  - Offres mises a jour: {ext.get('offres_mises_a_jour', 0)}")

    else:
        print("ECHEC de la collecte")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
