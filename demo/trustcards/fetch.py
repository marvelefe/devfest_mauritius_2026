"""One place for HTTP GETs, with an error that says what to do."""

from typing import Any

import httpx

START_SERVERS = (
    "Start the demo servers first, one terminal each: "
    "`make directory`, `make real`, `make fake`. Then run `make check`."
)


class ServerNotRunningError(RuntimeError):
    """A demo server isn't reachable."""


def get_json(url: str) -> Any:
    try:
        response = httpx.get(url, timeout=5)
    except httpx.ConnectError as error:
        raise ServerNotRunningError(f"Can't reach {url}. {START_SERVERS}") from error
    response.raise_for_status()
    return response.json()
