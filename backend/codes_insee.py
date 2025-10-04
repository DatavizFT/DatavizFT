# 🗺️ Codes INSEE des principales villes françaises

CODES_INSEE_VILLES = {
    # Grandes villes
    "nancy": "54395",
    "paris": "75056", 
    "lyon": "69123",
    "marseille": "13055",
    "toulouse": "31555",
    "nice": "06088",
    "nantes": "44109",
    "strasbourg": "67482",
    "montpellier": "34172",
    "bordeaux": "33063",
    "lille": "59350",
    "rennes": "35238",
    "reims": "51454",
    "le havre": "76351",
    "saint-etienne": "42218",
    "toulon": "83137",
    "grenoble": "38185",
    "dijon": "21231",
    "angers": "49007",
    "nimes": "30189",
    
    # Villes moyennes Grand Est
    "metz": "57463",
    "mulhouse": "68224",
    "colmar": "68066",
    "epinal": "88160",
    "chalons-en-champagne": "51108",
    "charleville-mezieres": "08105",
    "verdun": "55545",
    "bar-le-duc": "55029",
    "saint-dizier": "52448",
    "chaumont": "52121",
}

def get_code_insee(ville_nom):
    """Retourne le code INSEE d'une ville à partir de son nom"""
    ville_clean = ville_nom.lower().strip()
    return CODES_INSEE_VILLES.get(ville_clean, None)

def get_villes_disponibles():
    """Retourne la liste des villes disponibles"""
    return list(CODES_INSEE_VILLES.keys())

if __name__ == "__main__":
    print("🏙️ Villes disponibles avec codes INSEE:")
    for ville, code in CODES_INSEE_VILLES.items():
        print(f"   {ville.title()}: {code}")
    
    print(f"\nTest: Nancy -> {get_code_insee('nancy')}")
    print(f"Test: Paris -> {get_code_insee('paris')}")
    print(f"Test: ville inconnue -> {get_code_insee('ville_inexistante')}")