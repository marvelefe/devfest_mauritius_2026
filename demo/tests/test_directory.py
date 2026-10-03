import pytest
from starlette.testclient import TestClient

from trustcards import config, directory, fetch


def test_listings_newest_first_puts_fake_on_top():
    card_urls = [entry["card_url"] for entry in directory.listings()]
    assert card_urls == [config.FAKE.card_url, config.REAL.card_url]


def test_directory_app_serves_listings():
    response = TestClient(directory.create_app()).get("/directory.json")
    assert response.status_code == 200
    assert response.json() == directory.listings()


def test_fetch_listings_server_down_raises_clear_error():
    with pytest.raises(fetch.ServerNotRunningError, match="make directory"):
        directory.fetch_listings("translate", url="http://127.0.0.1:9/nothing")
