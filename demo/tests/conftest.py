import pytest

from trustcards import config, keys


@pytest.fixture(autouse=True)
def demo_keys(tmp_path, monkeypatch):
    """Fresh keys per test, so tests never touch the real keys/ folder."""
    monkeypatch.setattr(config, "KEYS_DIR", tmp_path / "keys")
    keys.generate_keys()


@pytest.fixture
def pinned():
    from trustcards.trust import pinned_verifier

    return pinned_verifier({config.REAL.key_id: keys.public_jwk(config.REAL.key_id)})
