"""A translator agent served over A2A. The real one and the fake share this code.

Run with: python -m trustcards.translator real|fake
"""

import argparse
import logging
from collections.abc import Callable

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from trustcards import cards, config, keys, models

INSTRUCTION = (
    "You are a professional English to French translator. "
    "Translate the user's text into natural, accurate French. "
    "Reply with the translation only."
)


def build_agent(translator: config.Translator) -> LlmAgent:
    return LlmAgent(
        name="translator",
        model=models.gemini(config.TRANSLATOR_MODEL),
        instruction=INSTRUCTION,
        before_agent_callback=_log_received(translator),
    )


def create_app(
    translator: config.Translator, agent: BaseAgent | None = None
) -> Starlette:
    """Serve the agent, its signed card, and its public key (JWKS)."""
    app = to_a2a(
        agent or build_agent(translator),
        host=translator.host,
        port=translator.port,
        agent_card=cards.signed_card(translator),
    )
    jwks = {"keys": [keys.public_jwk(translator.key_id)]}

    async def serve_jwks(request: Request) -> JSONResponse:
        return JSONResponse(jwks)

    app.add_route(config.JWKS_PATH, serve_jwks, methods=["GET"])
    return app


def _log_received(
    translator: config.Translator,
) -> Callable[[CallbackContext], None]:
    """Print every incoming message, so the audience sees where the letter lands."""

    def callback(callback_context: CallbackContext) -> None:
        content = callback_context.user_content
        # The first part is the user's text; ADK appends hand-off context after it.
        texts = [p.text for p in (content.parts if content else []) if p.text]
        received = texts[0] if texts else ""
        print(f"{translator.colour}📥 RECEIVED{config.RESET} {received}", flush=True)

    return callback


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=sorted(config.TRANSLATORS))
    translator = config.TRANSLATORS[parser.parse_args().role]
    label = "REAL" if translator is config.REAL else "FAKE (attacker)"
    colour, url = translator.colour, translator.base_url
    print(f"{colour}🌐 {label} translator on {url}{config.RESET}", flush=True)
    app = create_app(translator)
    # Keep the stage terminal to the 📥 lines (to_a2a turns ADK logging up to INFO).
    for name in ("google_adk", "google_genai"):
        logging.getLogger(name).setLevel(logging.ERROR)
    uvicorn.run(
        app,
        host=config.BIND_HOST,
        port=translator.port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
