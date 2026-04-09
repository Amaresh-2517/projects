"""Common crypto helpers for all four levels.

- Level 1/2 demos use these on the server for clarity.
- Level 3/4 move encryption to the browser; the server-side helpers
  remain for validation and educational code paths.
"""

import base64
import os
from dataclasses import dataclass
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives import hmac


# ------------ Key material ------------

def generate_rsa_keys() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate an RSA-2048 keypair for demo purposes."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    return private_key, private_key.public_key()


def serialize_public_key(public_key: rsa.RSAPublicKey) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


def serialize_private_key(private_key: rsa.RSAPrivateKey) -> str:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def load_public_key(pem: str) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(pem.encode(), backend=default_backend())


# ------------ Hybrid encryption (RSA-OAEP + AES-GCM) ------------

@dataclass
class HybridPayload:
    enc_key_b64: str
    iv_b64: str
    ciphertext_b64: str


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _unb64(data_b64: str) -> bytes:
    return base64.b64decode(data_b64.encode())


def hybrid_encrypt(plaintext: str, public_key: rsa.RSAPublicKey) -> HybridPayload:
    """Encrypt plaintext with fresh AES-256-GCM key, wrap key with RSA-OAEP."""
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    tag = encryptor.tag

    enc_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return HybridPayload(
        enc_key_b64=_b64(enc_key),
        iv_b64=_b64(iv + tag),  # tag is stored after IV for compactness
        ciphertext_b64=_b64(ciphertext),
    )


def hybrid_decrypt(payload: HybridPayload, private_key: rsa.RSAPrivateKey) -> str:
    aes_key = private_key.decrypt(
        _unb64(payload.enc_key_b64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    iv_tag = _unb64(payload.iv_b64)
    iv, tag = iv_tag[:12], iv_tag[12:]
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(_unb64(payload.ciphertext_b64)) + decryptor.finalize()
    return plaintext.decode()


# ------------ Signatures & HMAC ------------

def sign_payload(private_key: rsa.RSAPrivateKey, message: bytes) -> str:
    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return _b64(signature)


def verify_signature(public_key: rsa.RSAPublicKey, message: bytes, signature_b64: str) -> bool:
    try:
        public_key.verify(
            _unb64(signature_b64),
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def hmac_sha256(key: bytes, message: bytes) -> str:
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(message)
    return _b64(h.finalize())


def verify_hmac(key: bytes, message: bytes, tag_b64: str) -> bool:
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(message)
    try:
        h.verify(_unb64(tag_b64))
        return True
    except Exception:
        return False


__all__ = [
    "generate_rsa_keys",
    "serialize_public_key",
    "serialize_private_key",
    "load_public_key",
    "HybridPayload",
    "hybrid_encrypt",
    "hybrid_decrypt",
    "sign_payload",
    "verify_signature",
    "hmac_sha256",
    "verify_hmac",
]
