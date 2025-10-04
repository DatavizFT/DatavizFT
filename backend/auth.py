import httpx
from backend.config import TOKEN_URL, FRANCETRAVAIL_CLIENT_ID, FRANCETRAVAIL_CLIENT_SECRET

def get_token():
    print("Requesting new token...")
    
    # Vérification des credentials
    if not FRANCETRAVAIL_CLIENT_ID or not FRANCETRAVAIL_CLIENT_SECRET:
        raise ValueError("Client ID and Client Secret must be configured in .env file")
    
    try:
        response = httpx.post(
            TOKEN_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
                "client_id": FRANCETRAVAIL_CLIENT_ID,
                "client_secret": FRANCETRAVAIL_CLIENT_SECRET,
                "scope": "api_offresdemploiv2 o2dsoffre"
            }
        )
        
        print(f"Auth response status: {response.status_code}")
        
        if response.status_code == 400:
            error_details = response.json() if response.text else {"error": "Unknown error"}
            print(f"Authentication failed: {error_details}")
            raise ValueError(f"Authentication failed: {error_details.get('error_description', 'Invalid credentials')}")
        
        response.raise_for_status()
        token_data = response.json()
        print("Token received successfully")
        return token_data["access_token"]
        
    except httpx.HTTPStatusError as e:
        print(f"HTTP error during authentication: {e}")
        print(f"Response content: {e.response.text}")
        raise ValueError(f"Failed to authenticate with France Travail API: {e.response.status_code}")
    except Exception as e:
        print(f"Unexpected error during authentication: {e}")
        raise ValueError(f"Authentication error: {str(e)}")
