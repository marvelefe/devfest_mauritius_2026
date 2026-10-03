import pytest

from trustcards import assistant, cards, config, directory

BY_CARD_URL = {t.card_url: t for t in config.TRANSLATORS.values()}


@pytest.fixture
def fake_network(monkeypatch):
    """Serve the directory and signed cards from memory instead of HTTP."""

    def use(listed: list[config.Translator]) -> None:
        entries = [
            e for e in directory.listings() if BY_CARD_URL[e["card_url"]] in listed
        ]
        monkeypatch.setattr(directory, "fetch_listings", lambda skill: entries)
        monkeypatch.setattr(
            cards, "fetch_card", lambda url: cards.signed_card(BY_CARD_URL[url])
        )

    return use


def test_choose_translator_without_check_picks_first_listing_the_fake(fake_network):
    fake_network([config.REAL, config.FAKE])
    card = assistant.choose_translator()
    assert cards.endpoint_of(card) == config.FAKE.rpc_url


def test_choose_translator_with_pinned_check_skips_fake(fake_network, pinned):
    fake_network([config.REAL, config.FAKE])
    card = assistant.choose_translator(pinned)
    assert cards.endpoint_of(card) == config.REAL.rpc_url


def test_choose_translator_with_only_untrusted_cards_raises(fake_network, pinned):
    fake_network([config.FAKE])
    with pytest.raises(LookupError):
        assistant.choose_translator(pinned)
