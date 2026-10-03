"""Demo 2: only uses a translator whose card is signed by a key we pinned."""

from trustcards import config, keys
from trustcards.assistant import build_assistant
from trustcards.trust import pinned_verifier

# Provisioned out-of-band: we saved Lalang's public key before any card arrived.
TRUSTED_KEYS = {config.REAL.key_id: keys.public_jwk(config.REAL.key_id)}

root_agent = build_assistant(
    name="assistant_verified", verify=pinned_verifier(TRUSTED_KEYS)
)
