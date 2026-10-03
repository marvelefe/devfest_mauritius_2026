"""A tiny public agent directory. Anyone can list an agent here, newest first."""

from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from trustcards import config, fetch


def listings() -> list[dict[str, Any]]:
    entries = [
        {
            "name": config.CARD_NAME,
            "skill": config.TRANSLATE_SKILL,
            "card_url": t.card_url,
            "registered_at": t.registered_at,
        }
        for t in config.TRANSLATORS.values()
    ]
    return sorted(entries, key=lambda e: e["registered_at"], reverse=True)


def fetch_listings(skill: str, url: str = config.DIRECTORY_URL) -> list[dict[str, Any]]:
    return [entry for entry in fetch.get_json(url) if entry["skill"] == skill]


async def _directory(request: Request) -> JSONResponse:
    return JSONResponse(listings())


def create_app() -> Starlette:
    return Starlette(routes=[Route("/directory.json", _directory)])


if __name__ == "__main__":
    print(f"📒 Agent directory on {config.DIRECTORY_URL}")
    uvicorn.run(
        create_app(),
        host=config.BIND_HOST,
        port=config.DIRECTORY_PORT,
        log_level="warning",
    )
