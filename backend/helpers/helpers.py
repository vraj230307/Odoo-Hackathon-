# ============================================================
# Utility Helpers for Traveloop
# ============================================================

import secrets


def generate_public_token(length=32):
    """
    Generate a cryptographically secure random token string.
    Used for creating public share links for itineraries.

    Args:
        length: Number of random bytes (token will be twice this in hex chars).

    Returns:
        A unique hex string token.
    """
    return secrets.token_hex(length)
