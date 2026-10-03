from a2a.client.card_resolver import parse_agent_card
from google.adk.agents import BaseAgent
from starlette.testclient import TestClient

from trustcards import config, keys, translator


def test_translator_app_serves_verifiable_card_and_jwks(pinned):
    app = translator.create_app(config.REAL, agent=BaseAgent(name="stub"))
    with TestClient(app) as client:  # runs the lifespan that mounts A2A routes
        card = parse_agent_card(client.get(config.CARD_PATH).json())
        jwks = client.get(config.JWKS_PATH).json()

    pinned(card)
    assert jwks == {"keys": [keys.public_jwk(config.REAL.key_id)]}
