"""
DatavizFT - Point d'entrée principal
Exécute le pipeline de collecte et d'analyse des offres M1805
"""

import sys

from backend.pipelines.france_travail_m1805 import run_pipelineFT


def main_force():
    """Point d'entrée pour forcer l'exécution (ignore la vérification 24h)"""
    print("🔥 DATAVIZFT - FORÇAGE DU PIPELINE (ignore la vérification 24h)")

    try:
        # Exécuter le pipeline en forçant
        resultat = run_pipelineFT(forcer_execution=True)

        if resultat["success"]:
            print("\n🎉 PIPELINE FORCÉ EXÉCUTÉ AVEC SUCCÈS !")
            print(f"📊 {resultat['nb_offres']} offres M1805 collectées et analysées")
            print("📁 Fichiers générés dans le dossier data/")
        else:
            print(f"\n❌ ERREUR PIPELINE: {resultat['error']}")

    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Point d'entrée principal - Lance le pipeline complet"""
    print("🚀 DATAVIZFT - LANCEMENT DU PIPELINE")

    try:
        # Exécuter le pipeline complet avec vérification automatique
        resultat = run_pipelineFT()

        if resultat["success"]:
            if resultat.get("skipped"):
                print("\n⏭️ PIPELINE IGNORÉ (exécution récente détectée)")
                print(
                    f"📊 Dernière collecte: {resultat.get('nb_offres', 'N/A')} offres"
                )
                if resultat.get("dernier_fichier"):
                    import os

                    print(
                        f"📁 Fichier: {os.path.basename(resultat['dernier_fichier'])}"
                    )
            else:
                print("\n🎉 PIPELINE EXÉCUTÉ AVEC SUCCÈS !")
                print(
                    f"📊 {resultat['nb_offres']} offres M1805 collectées et analysées"
                )
                print("📁 Fichiers générés dans le dossier data/")
        else:
            print(f"\n❌ ERREUR PIPELINE: {resultat['error']}")

    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Vérifier les arguments pour le forçage
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        main_force()
    else:
        main()
