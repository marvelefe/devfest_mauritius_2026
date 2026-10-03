"""Demo 1: trusts whichever translator the directory lists first."""

from trustcards.assistant import build_assistant

root_agent = build_assistant(name="assistant")
