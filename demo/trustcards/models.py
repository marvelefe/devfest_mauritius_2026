"""Gemini models with retries, so a busy moment doesn't break the demo on stage."""

from google.adk.models.google_llm import Gemini
from google.genai import types

from trustcards import config


def gemini(model: str) -> Gemini:
    return Gemini(
        model=model, retry_options=types.HttpRetryOptions(**config.MODEL_RETRY)
    )
