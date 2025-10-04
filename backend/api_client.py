import httpx
import json
import os
from datetime import datetime
from backend.auth import get_token
from backend.config import API_BASE_URL
from backend.codes_insee import get_code_insee, get_villes_disponibles

def fetch_offres(code_rome="M1805", range_param="0-190", commune="Nancy"):
    print("=" * 60)
    print(f"🔍 FETCH_OFFRES APPELÉ !")
    print(f"   code_rome: {code_rome}")
    print(f"   commune: {commune}")
    print(f"   range: {range_param}")
    print("=" * 60)
    try:
        token = get_token()
        print("apres get_token dans api_client")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "DatavizFT/1.0"
        }
        # Approche hybride pour respecter la distance géographique
        code_insee = get_code_insee(commune)
        if code_insee:
            print(f"🏙️ Ville '{commune}' -> Code INSEE: {code_insee} (recherche locale)")
            lieu_param = {"commune": code_insee}
        else:
            print(f"🏙️ Ville '{commune}' non reconnue -> recherche élargie par département")
            # Essayer de deviner le département à partir du nom
            lieu_param = {"lieuTravail": commune}
        
        # Construction des paramètres SANS origine pour avoir France Travail + Partenaires
        params = {
            "codeROME": code_rome,
            "range": range_param,
            # Pas de paramètre "origine" = toutes les offres (FT + Partenaires)
            "origineOffre": "1",  # Inclut les offres des partenaires
            **lieu_param  # Ajoute soit commune (code INSEE) soit lieuTravail
        }
        
        # Filtrer les paramètres None ou vides
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        
        url = f"{API_BASE_URL}/offres/search"
        print(f"Calling API: {url} with params: {params}")
        
        response = httpx.get(url, headers=headers, params=params)
        
        # L'API France Travail retourne 206 (Partial Content) pour les résultats paginaés
        if response.status_code in [200, 206]:
            data = response.json()
            nb_offres = len(data.get('resultats', []))
            print(f"✅ {nb_offres} offres récupérées")
            
            # Enregistrement des résultats au format JSON
            try:
                # Créer le dossier de sauvegarde s'il n'existe pas
                save_dir = "data/json_results"
                os.makedirs(save_dir, exist_ok=True)
                
                # Nom du fichier avec timestamp et paramètres
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"offres_{code_rome}_{commune}_{timestamp}.json"
                filepath = os.path.join(save_dir, filename)
                
                # Ajouter des métadonnées aux résultats
                save_data = {
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "parametres": {
                            "code_rome": code_rome,
                            "commune": commune,
                            "range": range_param
                        },
                        "nb_resultats": len(data.get('resultats', [])),
                        "url_api": url,
                        "params_api": params
                    },
                    "resultats": data
                }
                
                # Sauvegarder le fichier JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Résultats sauvegardés dans: {filepath}")
                
            except Exception as save_error:
                print(f"⚠️ Erreur lors de la sauvegarde JSON: {save_error}")
            
            return data
        else:
            print("Erreur API:", response.status_code, response.text)
            response.raise_for_status()
        
    except ValueError as e:
        print(f"Error in fetch_offres: {e}")
        return {"error": str(e), "offres": []}
    except Exception as e:
        print(f"Unexpected error in fetch_offres: {e}")
        return {"error": f"API Error: {str(e)}", "offres": []}
