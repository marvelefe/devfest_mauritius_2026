"""The Assistant: a fast generalist that hands translation to a specialist agent.

Picking the translator is deterministic: the first directory listing wins.
With a verifier, the first listing whose card passes the check wins.
"""

from a2a.types import AgentCard
from a2a.utils.signing import SignatureVerificationError
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from trustcards import cards, config, directory, models
from trustcards.trust import Verifier

INSTRUCTION = (
    "You are a helpful assistant. For any translation request, transfer to the "
    "`translator` agent with the full text. Never translate it yourself."
)


def choose_translator(verify: Verifier | None = None) -> AgentCard:
    for listing in directory.fetch_listings(config.TRANSLATE_SKILL):
        card = cards.fetch_card(listing["card_url"])
        endpoint = cards.endpoint_of(card)
        if verify is None:  # no check: take whatever the directory lists first
            print(f"⚠️  Using {endpoint} (first listing, not checked)", flush=True)
            return card
        try:
            verify(card)
        except SignatureVerificationError as error:
            print(f"🛑 Skipped {endpoint}: {error}", flush=True)
            continue
        print(f"✅ Verified {endpoint}", flush=True)
        return card
    raise LookupError("No trustworthy translator found in the directory.")


def build_assistant(name: str, verify: Verifier | None = None) -> LlmAgent:
    card = choose_translator(verify)
    # Pass the card object we checked, not a URL, so there is no second fetch.
    translator = RemoteA2aAgent(name="translator", agent_card=card)
    return LlmAgent(
        name=name,
        model=models.gemini(config.ASSISTANT_MODEL),
        instruction=INSTRUCTION,
        sub_agents=[translator],
    )
