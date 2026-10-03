import pytest
from a2a.client.card_resolver import parse_agent_card
from a2a.server.request_handlers.response_helpers import agent_card_to_dict
from a2a.utils.signing import InvalidSignaturesError, NoSignatureError

from trustcards import cards, config


def test_pinned_check_real_card_passes(pinned):
    pinned(cards.signed_card(config.REAL))


def test_pinned_check_card_signed_by_attacker_is_rejected(pinned):
    with pytest.raises(InvalidSignaturesError):
        pinned(cards.signed_card(config.FAKE))


def test_pinned_check_unsigned_card_is_rejected(pinned):
    with pytest.raises(NoSignatureError):
        pinned(cards.build_card(config.REAL))


def test_pinned_check_tampered_endpoint_is_rejected(pinned):
    card = cards.signed_card(config.REAL)
    card.supported_interfaces[0].url = config.FAKE.rpc_url
    with pytest.raises(InvalidSignaturesError):
        pinned(card)


def test_served_card_round_trip_still_verifies(pinned):
    """The server adds legacy fields to the JSON; the signature must survive."""
    served_json = agent_card_to_dict(cards.signed_card(config.REAL))
    pinned(parse_agent_card(served_json))
