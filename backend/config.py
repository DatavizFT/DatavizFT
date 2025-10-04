from dotenv import load_dotenv
import os

load_dotenv()

FRANCETRAVAIL_CLIENT_ID = os.getenv("FRANCETRAVAIL_CLIENT_ID")
FRANCETRAVAIL_CLIENT_SECRET = os.getenv("FRANCETRAVAIL_CLIENT_SECRET")
TOKEN_URL = "https://francetravail.io/connexion/oauth2/access_token?realm=%2Fpartenaire"
API_BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2"
