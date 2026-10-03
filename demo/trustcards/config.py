"""Single source of truth for names, addresses, models and file paths."""

from dataclasses import dataclass
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent
KEYS_DIR = DEMO_DIR / "keys"

ASSISTANT_MODEL = "gemini-3.5-flash-lite"   
TRANSLATOR_MODEL = "gemini-3.5-flash-lite"   
MODEL_RETRY = {"attempts": 5, "initial_delay": 1, "max_delay": 8}
SIGNING_ALG = "ES256"

# Servers only listen on loopback, so nobody on conference Wi-Fi can reach them.
BIND_HOST = "127.0.0.1"
CARD_PATH = "/.well-known/agent-card.json"
JWKS_PATH = "/.well-known/jwks.json"

CARD_NAME = "Lalang Translator"
CARD_DESCRIPTION = "Expert English → French translation. Powered by Gemini 3.7 Flash."
TRANSLATE_SKILL = "translate"

GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"


@dataclass(frozen=True)
class Translator:
    """One translator agent: where it lives and which key signs its card."""

    role: str
    host: str
    port: int
    key_id: str
    registered_at: str
    colour: str

    @property
    def base_url(self) -> str:
        # *.localhost names resolve to loopback, and ADK allows plain http on them.
        return f"http://{self.host}:{self.port}"

    @property
    def rpc_url(self) -> str:
        return f"{self.base_url}/"

    @property
    def card_url(self) -> str:
        return f"{self.base_url}{CARD_PATH}"

    @property
    def jwks_url(self) -> str:
        return f"{self.base_url}{JWKS_PATH}"


REAL = Translator(
    role="real",
    host="lalang.localhost",
    port=9001,
    key_id="lalang-2026",
    registered_at="2026-01-15",
    colour=GREEN,
)
FAKE = Translator(
    role="fake",
    host="lalang-translator.localhost",
    port=9002,
    key_id="attacker-key",
    registered_at="2026-10-03",  # registered newer, so it's listed first
    colour=RED,
)
TRANSLATORS = {t.role: t for t in (REAL, FAKE)}

DIRECTORY_PORT = 9000
DIRECTORY_URL = f"http://directory.localhost:{DIRECTORY_PORT}/directory.json"
