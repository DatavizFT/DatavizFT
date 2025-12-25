"""
Script pour examiner la structure d'une offre
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
    """Examine la structure d'une offre"""
    
    print("EXAMEN STRUCTURE D'UNE OFFRE")
    print("=" * 40)
    
    # Configuration
    config = Config()
    
    # Connexion directe à MongoDB
    client = AsyncIOMotorClient(config.get_mongodb_url())
    db = client[config.MONGODB_DATABASE]
    
    try:
        offres_collection = db.offres
        
        # Récupérer une offre
        offre = await offres_collection.find_one({})
        
        if not offre:
            print("❌ Aucune offre trouvée")
            return
        
        print(f"📄 OFFRE ID: {offre.get('id', 'Unknown')}")
        print(f"Intitulé: {offre.get('intitule', 'Unknown')}")
        print()
        
        print("📋 CHAMPS DISPONIBLES:")
        for cle in sorted(offre.keys()):
            valeur = offre[cle]
            if isinstance(valeur, str):
                valeur_str = valeur[:100] + "..." if len(valeur) > 100 else valeur
            elif isinstance(valeur, list):
                valeur_str = f"[{len(valeur)} éléments]"
            elif isinstance(valeur, dict):
                valeur_str = f"dict avec {len(valeur)} clés"
            else:
                valeur_str = str(valeur)
            
            print(f"  {cle}: {valeur_str}")
        
        print()
        
        # Vérifier spécifiquement les champs de compétences
        print("🔍 CHAMPS RELATIFS AUX COMPETENCES:")
        champs_competences = [
            'competences_extraites', 
            'competences_detectees',
            'description',
            'qualificationLibelle',
            'secteurActiviteLibelle'
        ]
        
        for champ in champs_competences:
            if champ in offre:
                valeur = offre[champ]
                print(f"✅ {champ}: {type(valeur).__name__} - {valeur}")
            else:
                print(f"❌ {champ}: non présent")
        
        print()
        
        # Examiner le contenu textuel pour l'extraction de compétences
        print("📝 CONTENU TEXTUEL DE L'OFFRE:")
        description = offre.get('description', '')
        if description:
            print(f"Description ({len(description)} caractères):")
            print(f"  {description[:300]}...")
        else:
            print("❌ Pas de description")
        
        # Autres champs textuels
        autres_champs = ['qualificationLibelle', 'experienceLibelle']
        for champ in autres_champs:
            valeur = offre.get(champ, '')
            if valeur:
                print(f"{champ}: {valeur}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())