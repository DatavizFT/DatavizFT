"""
Script pour examiner toutes les collections liées aux compétences
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
    """Examine le contenu des collections de compétences"""
    
    print("ANALYSE DES COLLECTIONS DE COMPETENCES")
    print("=" * 60)
    
    # Configuration
    config = Config()
    
    # Connexion directe à MongoDB
    client = AsyncIOMotorClient(config.get_mongodb_url())
    db = client[config.MONGODB_DATABASE]
    
    try:
        # Lister toutes les collections
        collections = await db.list_collection_names()
        print(f"Collections disponibles: {collections}")
        print()
        
        # 1. Analyser stats_competences
        print("📊 COLLECTION: stats_competences")
        print("-" * 40)
        stats_collection = db.stats_competences
        nb_stats = await stats_collection.count_documents({})
        print(f"Nombre de documents: {nb_stats}")
        
        # Regarder le dernier document
        dernier_doc = await stats_collection.find_one(sort=[("date_analyse", -1)])
        if dernier_doc:
            print(f"Dernière analyse: {dernier_doc.get('date_analyse')}")
            print(f"Offres analysées: {dernier_doc.get('nb_offres_analysees', 0)}")
            top_comp = dernier_doc.get("top_competences", [])
            print(f"Compétences trouvées: {len(top_comp)}")
            if len(top_comp) > 0:
                print("Top 5:")
                for comp in top_comp[:5]:
                    print(f"  - {comp.get('competence')}: {comp.get('nb_occurrences')}")
        print()
        
        # 2. Analyser competences_detections
        print("🔍 COLLECTION: competences_detections")
        print("-" * 40)
        competences_collection = db.competences_detections
        nb_competences = await competences_collection.count_documents({})
        print(f"Nombre de documents: {nb_competences}")
        
        if nb_competences > 0:
            # Échantillon de documents
            sample = await competences_collection.find({}).limit(3).to_list(3)
            for i, doc in enumerate(sample, 1):
                print(f"  Exemple {i}:")
                print(f"    Offre ID: {doc.get('offre_id', 'Unknown')}")
                print(f"    Compétences: {doc.get('competences_extraites', [])}")
                print(f"    Date: {doc.get('date_creation', 'Unknown')}")
        print()
        
        # 3. Analyser offres (échantillon)
        print("📄 COLLECTION: offres (échantillon)")
        print("-" * 40)
        offres_collection = db.offres
        nb_offres = await offres_collection.count_documents({})
        print(f"Nombre total d'offres: {nb_offres}")
        
        # Vérifier si les offres ont des compétences extraites
        offres_avec_competences = await offres_collection.count_documents(
            {"competences_extraites": {"$exists": True, "$ne": []}}
        )
        print(f"Offres avec compétences extraites: {offres_avec_competences}")
        
        # Échantillon d'offres avec compétences
        if offres_avec_competences > 0:
            offre_sample = await offres_collection.find_one(
                {"competences_extraites": {"$exists": True, "$ne": []}}
            )
            if offre_sample:
                print(f"Exemple d'offre avec compétences:")
                print(f"  ID: {offre_sample.get('id', 'Unknown')}")
                print(f"  Compétences: {offre_sample.get('competences_extraites', [])}")
        print()
        
        # 4. Analyser les compétences uniques dans les offres
        print("📈 ANALYSE DES COMPETENCES DANS LES OFFRES")
        print("-" * 40)
        
        # Pipeline pour compter les compétences
        pipeline = [
            {"$unwind": "$competences_extraites"},
            {"$group": {"_id": "$competences_extraites", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        try:
            cursor = offres_collection.aggregate(pipeline)
            results = await cursor.to_list(10)
            
            if results:
                print("Top 10 des compétences les plus demandées:")
                for i, result in enumerate(results, 1):
                    print(f"  {i:2d}. {result['_id']}: {result['count']} occurrences")
            else:
                print("❌ Aucune compétence trouvée dans les offres")
        except Exception as e:
            print(f"❌ Erreur lors de l'agrégation: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Analyse terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())