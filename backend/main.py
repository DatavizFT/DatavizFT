from fastapi import FastAPI, HTTPException, Query
from backend.api_client import fetch_offres

app = FastAPI()
print("api started")

@app.get("/offres")
def get_offres(code_rome: str = "M1805", commune: str = "Nancy", range_param: str = "0-149"):
    print("\n" + "🌟" * 30)
    print("🚀 ENDPOINT /offres APPELÉ !")
    print(f"📋 Paramètres reçus:")
    print(f"   - code_rome: {code_rome}")
    print(f"   - commune: {commune}")
    print(f"   - range_param: {range_param}")
    print("🌟" * 30)
    try:
        print("🔄 Appel de fetch_offres()...")
        result = fetch_offres(code_rome, range_param, commune)
        print("✅ fetch_offres() a retourné un résultat : nombre d'offres =", len(result.get('resultats', [])))
        # Si fetch_offres retourne une erreur, la gérer
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=f"API Error: {result['error']}")
        return result
    except Exception as e:
        print(f"Error in get_offres endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "DatavizFT API is running", "status": "ok"}
