"""Build, sign and fetch Agent Cards."""

from a2a.client.card_resolver import parse_agent_card
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from a2a.utils.signing import create_agent_card_signer

from trustcards import config, fetch, keys


def build_card(translator: config.Translator) -> AgentCard:
    """The same name and description for both translators. Only the URL differs."""
    return AgentCard(
        name=config.CARD_NAME,
        description=config.CARD_DESCRIPTION,
        version="1.0.0",
        supported_interfaces=[
            AgentInterface(
                url=translator.rpc_url,
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        capabilities=AgentCapabilities(),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id=config.TRANSLATE_SKILL,
                name="Translate text",
                description="Translates English text into natural French.",
                tags=[config.TRANSLATE_SKILL, "french"],
            )
        ],
    )


def signed_card(translator: config.Translator) -> AgentCard:
    """Seal the card with the translator's own private key.

    The attacker signs too, with *their* key and *their* JWKS URL.
    """
    sign = create_agent_card_signer(
        signing_key=keys.private_key_pem(translator.key_id),
        protected_header={
            "alg": config.SIGNING_ALG,  # always set: the SDK defaults to HS256
            "typ": "JOSE",
            "kid": translator.key_id,
            "jku": translator.jwks_url,
        },
    )
    return sign(build_card(translator))


def fetch_card(card_url: str) -> AgentCard:
    return parse_agent_card(fetch.get_json(card_url))


def endpoint_of(card: AgentCard) -> str:
    """Where tasks sent to this agent actually go."""
    return card.supported_interfaces[0].url
