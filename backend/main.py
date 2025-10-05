"""
DatavizFT - Point d'entrée principal
Exécute le pipeline de collecte et d'analyse des offres M1805
"""

from backend.pipelineFT import run_pipeline

def main():
    """Point d'entrée principal - Lance le pipeline complet"""
    print("🚀 DATAVIZFT - LANCEMENT DU PIPELINE")
    
    try:
        # Exécuter le pipeline complet
        resultat = run_pipeline()
        
        if resultat["success"]:
            print("\n🎉 PIPELINE EXÉCUTÉ AVEC SUCCÈS !")
            print(f"📊 {resultat['nb_offres']} offres M1805 collectées et analysées")
            print(f"📁 Fichiers générés dans le dossier data/")
        else:
            print(f"\n❌ ERREUR PIPELINE: {resultat['error']}")
            
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
