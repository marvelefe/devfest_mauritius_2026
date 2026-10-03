"""Demo signing keys: generate once, then load by key id.

Each key id gets two files in ``keys/``:
- ``<kid>.pem``       private key, used only by the agent that owns it
- ``<kid>.pub.json``  public key (JWK), safe to publish or pin
"""

import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

from trustcards import config


def generate_keys(force: bool = False) -> None:
    """Create an ES256 key pair for every translator (skips existing keys)."""
    config.KEYS_DIR.mkdir(exist_ok=True)
    for translator in config.TRANSLATORS.values():
        pem_path = config.KEYS_DIR / f"{translator.key_id}.pem"
        if pem_path.exists() and not force:
            continue
        private_key = ec.generate_private_key(ec.SECP256R1())
        pem_path.write_bytes(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        public_jwk = ECAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
        public_jwk.update(kid=translator.key_id, alg=config.SIGNING_ALG, use="sig")
        pub_path = config.KEYS_DIR / f"{translator.key_id}.pub.json"
        pub_path.write_text(json.dumps(public_jwk, indent=2))
        print(f"Created {pem_path.name} and {pub_path.name}")


def private_key_pem(key_id: str) -> bytes:
    return _read(f"{key_id}.pem").read_bytes()


def public_jwk(key_id: str) -> dict[str, Any]:
    return json.loads(_read(f"{key_id}.pub.json").read_text())


def _read(filename: str) -> Path:
    path = config.KEYS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run `make keys` first.")
    return path


if __name__ == "__main__":
    generate_keys()
