import asyncio
import sys
import os
from datetime import datetime

# Configuration des imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from database.connection import DatabaseConnection
except ImportError:
    import backend.database
    from backend.database.connection import DatabaseConnection

async def analyser_dates_cloture():
    """Analyse les dates de clôture pour voir QUAND les offres ont été clôturées"""
    db_conn = DatabaseConnection()
    await db_conn.connect()
    
    collection = db_conn.async_db.offres
    
    # Récupérer quelques offres clôturées avec leurs dates
    offres_cloturees = await collection.find({
        "source": "france_travail",
        "date_cloture": {"$exists": True, "$ne": None}
    }).limit(10).to_list(None)
    
    print(f"📅 ANALYSE DES DATES DE CLÔTURE:")
    print(f"=" * 50)
    
    for i, offre in enumerate(offres_cloturees[:5], 1):
        date_collecte = offre.get('date_collecte', 'Non définie')
        date_cloture = offre.get('date_cloture', 'Non définie')
        source_id = offre.get('source_id', 'Non défini')
        
        print(f"{i}. Offre {source_id}")
        print(f"   📥 Collectée le: {date_collecte}")
        print(f"   🔒 Clôturée le: {date_cloture}")
        print()
    
    # Statistiques par date de clôture
    pipeline = [
        {"$match": {
            "source": "france_travail",
            "date_cloture": {"$exists": True, "$ne": None}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_cloture"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    dates_clotures = await collection.aggregate(pipeline).to_list(None)
    
    print(f"📊 RÉPARTITION DES CLÔTURES PAR DATE:")
    for stat in dates_clotures:
        print(f"   {stat['_id']}: {stat['count']} offres clôturées")
    
    await db_conn.close()

if __name__ == "__main__":
    asyncio.run(analyser_dates_cloture())