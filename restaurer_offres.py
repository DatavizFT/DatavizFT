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

async def restaurer_offres_cloturees():
    """Restaure les offres erronnément clôturées le 18 octobre 2025"""
    db_conn = DatabaseConnection()
    await db_conn.connect()
    
    collection = db_conn.async_db.offres
    
    # 1. Identifier les offres clôturées le 18 octobre 2025
    offres_a_restaurer = await collection.find({
        "source": "france_travail",
        "date_cloture": {
            "$gte": datetime(2025, 10, 18, 0, 0, 0),
            "$lt": datetime(2025, 10, 19, 0, 0, 0)
        }
    }).to_list(None)
    
    if not offres_a_restaurer:
        print("❌ Aucune offre à restaurer trouvée")
        await db_conn.close()
        return
    
    print(f"🔍 {len(offres_a_restaurer)} offres clôturées le 18/10/2025 trouvées")
    
    # 2. Demander confirmation
    print(f"\n⚠️  ATTENTION : Voulez-vous restaurer ces {len(offres_a_restaurer)} offres ?")
    print("   Cela va supprimer leur date_cloture pour les rendre actives à nouveau.")
    
    # Pour le moment, juste afficher les infos sans modifier
    print(f"\n📊 APERÇU DES OFFRES À RESTAURER :")
    for i, offre in enumerate(offres_a_restaurer[:10], 1):
        print(f"   {i}. {offre['source_id']} - {offre.get('intitule', 'Sans titre')[:50]}...")
        print(f"      Clôturée le: {offre['date_cloture']}")
    
    if len(offres_a_restaurer) > 10:
        print(f"   ... et {len(offres_a_restaurer) - 10} autres")
    
    print(f"\n🔧 Pour restaurer, décommentez la section de mise à jour dans le script")
    
    # SECTION DE RESTAURATION (commentée pour sécurité)
    """
    # Décommentez cette section pour restaurer les offres
    confirm = input("\\nTaper 'RESTAURER' pour confirmer : ")
    if confirm == "RESTAURER":
        result = await collection.update_many(
            {
                "source": "france_travail",
                "date_cloture": {
                    "$gte": datetime(2025, 10, 18, 0, 0, 0),
                    "$lt": datetime(2025, 10, 19, 0, 0, 0)
                }
            },
            {
                "$unset": {"date_cloture": ""}
            }
        )
        print(f"✅ {result.modified_count} offres restaurées avec succès")
    else:
        print("❌ Restauration annulée")
    """
    
    await db_conn.close()

if __name__ == "__main__":
    asyncio.run(restaurer_offres_cloturees())