import os 
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
 
OAUTH2_PROVIDERS={
    "facebook":{
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
        "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "user_info_url": "https://graph.facebook.com/me?fields=id,name,email,first_name,last_name",
        "scope": "email",
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI")
    }
}

def get_provider_config(provider: str):
    if provider not in OAUTH2_PROVIDERS:
        raise ValueError(f"Unspported provider: {provider}")
    return OAUTH2_PROVIDERS[provider]