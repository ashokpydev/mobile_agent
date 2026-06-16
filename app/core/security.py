from cryptography.fernet import Fernet, InvalidToken


class FieldEncryptor:
    """Small encryption wrapper for sensitive fields at rest."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(self._normalize_key(key))

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt value") from exc

    @staticmethod
    def _normalize_key(key: str) -> bytes:
        if len(key) == 44:
            return key.encode("utf-8")
        return Fernet.generate_key()

