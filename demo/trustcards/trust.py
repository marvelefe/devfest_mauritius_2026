"""Verify Agent Card signatures against keys we already trust ("pinning")."""

from collections.abc import Callable
from typing import Any

from a2a.types import AgentCard
from a2a.utils.signing import create_signature_verifier
from jwt import PyJWK
from jwt.exceptions import PyJWKError

from trustcards import config

Verifier = Callable[[AgentCard], None]


def pinned_verifier(trusted_keys: dict[str, dict[str, Any]]) -> Verifier:
    """Build a verifier that only accepts keys provisioned in advance.

    The card's own ``jku`` is ignored on purpose: an attacker writes the card,
    so they would choose where the key comes from.
    """

    def get_key(kid: str | None, jku: str | None) -> PyJWK:
        if kid not in trusted_keys:
            # A PyJWTError subclass: the SDK moves on to the next signature and,
            # if none verify, raises InvalidSignaturesError (fails closed).
            raise PyJWKError(f"untrusted key: {kid}")
        return PyJWK(trusted_keys[kid])

    # Unsigned cards raise NoSignatureError, so stripping the signature doesn't help.
    return create_signature_verifier(
        key_provider=get_key, algorithms=[config.SIGNING_ALG]
    )
