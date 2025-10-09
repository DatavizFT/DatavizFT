#!/usr/bin/env python3
"""
Script de lancement du pipeline DatavizFT
Usage:
  python run_pipeline.py                 # Exécution normale (vérification 24h)
  python run_pipeline.py --force         # Forcer l'exécution
  python run_pipeline.py --limit 50      # Limiter à 50 offres
  python run_pipeline.py --stats         # Afficher les statistiques
"""

import argparse
from backend.pipelines.france_travail_m1805 import (
    run_pipelineFT, 
    run_pipeline_avec_limite, 
    PipelineM1805
)


def main():
    parser = argparse.ArgumentParser(description='Pipeline DatavizFT M1805')
    
    parser.add_argument(
        '--force', 
        action='store_true', 
        help='Forcer l\'exécution (ignore la vérification 24h)'
    )
    
    parser.add_argument(
        '--limit', 
        type=int, 
        help='Limiter le nombre d\'offres collectées'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true', 
        help='Afficher les statistiques du pipeline'
    )

    args = parser.parse_args()

    if args.stats:
        # Afficher les statistiques
        pipeline = PipelineM1805()
        stats = pipeline.obtenir_statistiques_pipeline()
        
        print("📊 STATISTIQUES PIPELINE M1805")
        print("=" * 50)
        print(f"Code ROME: {stats['code_rome']}")
        print(f"Catégories de compétences: {stats['nb_categories_competences']}")
        print(f"Compétences totales: {stats['nb_competences_total']}")
        print(f"Stockage: {stats['stockage']}")
        return

    if args.limit:
        # Exécution avec limite
        print(f"🎯 PIPELINE AVEC LIMITE: {args.limit} offres maximum")
        resultat = run_pipeline_avec_limite(args.limit)
    else:
        # Exécution normale ou forcée
        resultat = run_pipelineFT(forcer_execution=args.force)

    # Afficher les résultats
    if resultat["success"]:
        if resultat.get("skipped"):
            print(f"⏭️ Pipeline ignoré: {resultat.get('raison', 'Exécution récente')}")
        else:
            print(f"✅ Pipeline réussi: {resultat['nb_offres']} offres traitées")
    else:
        print(f"❌ Pipeline échoué: {resultat.get('error', 'Erreur inconnue')}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())