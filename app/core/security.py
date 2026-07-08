import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class FieldEncryptor:
    """Small encryption wrapper for sensitive fields at rest."""

    def __init__(self, key: str) -> None:
        try:
            self._fernet = Fernet(key.encode("utf-8"))
        except Exception as exc:
            raise ValueError(
                "Invalid encryption key: expected a 32-byte urlsafe base64-encoded Fernet key"
            ) from exc

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt value") from exc


def derive_fernet_key(secret: str) -> str:
    """Turn any configured secret string into a valid Fernet key, deterministically.

    `settings.encryption_key` is an operator-supplied secret like the other signing
    keys, not a pre-generated base64 Fernet key, so it can't be handed to Fernet()
    directly.
    """
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8")


@lru_cache
def get_field_encryptor() -> FieldEncryptor:
    return FieldEncryptor(derive_fernet_key(settings.encryption_key))

