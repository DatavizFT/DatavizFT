"""
Script pour examiner le contenu de la collection stats_competences
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le backend au path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

async def main():
    """Examine le contenu de stats_competences"""
    
    print("ANALYSE DE LA COLLECTION stats_competences")
    print("=" * 50)
    
    # Configuration
    config = Config()
    
    # Connexion directe à MongoDB
    client = AsyncIOMotorClient(config.get_mongodb_url())
    db = client[config.MONGODB_DATABASE]
    
    try:
        # Collection stats_competences
        collection = db.stats_competences
        
        # Compter les documents
        nb_docs = await collection.count_documents({})
        print(f"Nombre de documents: {nb_docs}")
        print()
        
        if nb_docs == 0:
            print("❌ Aucun document trouvé dans stats_competences")
            return
        
        print("📋 DOCUMENTS DANS LA COLLECTION:")
        print("-" * 40)
        
        # Lister tous les documents
        cursor = collection.find({})
        i = 0
        async for doc in cursor:
            i += 1
            print(f"\n📄 DOCUMENT {i}:")
            
            # Informations principales
            for cle in ["_id", "periode_analysee", "date_analyse", "nb_offres_analysees"]:
                if cle in doc:
                    valeur = doc[cle]
                    if isinstance(valeur, datetime):
                        valeur = valeur.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"   {cle}: {valeur}")
            
            # Top compétences
            top_comp = doc.get("top_competences", [])
            print(f"   Nombre de compétences analysées: {len(top_comp)}")
            
            if top_comp:
                print("   🏆 TOP 10 COMPETENCES:")
                for j, comp in enumerate(top_comp[:10], 1):
                    nom = comp.get("competence", "Unknown")
                    count = comp.get("nb_occurrences", 0)
                    pct = comp.get("pourcentage", 0)
                    print(f"      {j:2d}. {nom}: {count} occurrences ({pct}%)")
            
            # NOUVELLES STATISTIQUES PAR CATÉGORIE
            stats_categories = doc.get("statistiques_par_categorie", {})
            if stats_categories:
                print(f"   📊 Statistiques par catégorie: {len(stats_categories)} catégories")
                
                # Trier les catégories par pourcentage
                categories_triees = sorted(
                    stats_categories.items(), 
                    key=lambda x: x[1].get("pourcentage_offres", 0), 
                    reverse=True
                )
                
                print("   🏆 Top 5 catégories:")
                for nom_cat, stats_cat in categories_triees[:5]:
                    pct = stats_cat.get("pourcentage_offres", 0)
                    nb_offres = stats_cat.get("nb_offres_avec_categorie", 0)
                    nb_techs = stats_cat.get("nb_technologies_detectees", 0)
                    print(f"     - {nom_cat}: {pct}% ({nb_offres} offres, {nb_techs} techs)")
            
            # Évolution temporelle si disponible  
            evolution = doc.get("evolution_temporelle", [])
            if evolution:
                print(f"   📈 Points d'évolution temporelle: {len(evolution)}")
                if len(evolution) > 0:
                    dernier_point = evolution[-1]
                    print(f"      Dernier point: {dernier_point}")
            
            # Répartition mensuelle si disponible
            repartition = doc.get("repartition_mensuelle", [])
            if repartition:
                print(f"   📊 Répartition mensuelle: {len(repartition)} périodes")
        
        print("\n" + "=" * 50)
        print("✅ Analyse terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())