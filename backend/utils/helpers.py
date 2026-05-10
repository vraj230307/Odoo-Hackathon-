import secrets

def generate_public_token():
    return secrets.token_urlsafe(32)