# services/stegano_crypto.py

import base64
from typing import Optional
import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from app.core.config import get_settings

ALPH = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
settings = get_settings()

class SteganoCryptoService:
    def __init__(self):
        master_key_hex = settings.CRYPTO_MASTER_KEY
        if not master_key_hex:
            raise RuntimeError(
                f"Generate a 32-byte random key and set it as hex in your environment."
            )

        try:
            master_key = bytes.fromhex(master_key_hex)
        except ValueError as exc:
            raise RuntimeError(f"The key must be a valid hex string.") from exc

        if len(master_key) != 32:
            raise RuntimeError(f"The key must be 32 bytes (64 hex chars).")

        self._master_key = master_key

    def _derive_key(self) -> bytes:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=str().encode("utf-8"),
            info=b"stegano-chacha20-key-derivation",
        )
        return hkdf.derive(self._master_key)

    def _caesar_encode(self, uid: str, shift=5):
        print("Encoding UID:", uid);
        return "".join(ALPH[(ALPH.index(c)+shift) % len(ALPH)] if c in ALPH else c for c in uid)

    def _caesar_decode(self, enc: str, shift=5):
        return "".join(ALPH[(ALPH.index(c)-shift) % len(ALPH)] if c in ALPH else c for c in enc)

    def encrypt_for_user(
        self,
        user_id: str | int,
        aad: Optional[str] = None,
    ) -> str:
        key = self._derive_key()
        chacha = ChaCha20Poly1305(key)

        nonce = os.urandom(12)
        aad_bytes = aad.encode("utf-8") if aad else None
        message = self._caesar_encode(str(user_id))
        ciphertext = chacha.encrypt(nonce, message.encode("utf-8"), aad_bytes)

        combined = nonce + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    def decrypt_for_user(
        self,
        payload_b64: str,
        aad: Optional[str] = None,
    ) -> str:
        key = self._derive_key()
        chacha = ChaCha20Poly1305(key)

        try:
            combined = base64.b64decode(payload_b64)
        except Exception as exc:
            raise ValueError("Invalid base64 payload") from exc

        if len(combined) < 12 + 16:
            raise ValueError("Payload too short")

        nonce = combined[:12]
        ciphertext = combined[12:]
        aad_bytes = aad.encode("utf-8") if aad else None

        try:
            plaintext = chacha.decrypt(nonce, ciphertext, aad_bytes)
            message = self._caesar_decode(plaintext.decode("utf-8"))
        except Exception as exc:
            raise ValueError("Authentication failed") from exc

        return message

SteganoCryptoService = SteganoCryptoService()