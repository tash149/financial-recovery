"""Gemini client. The API key is read from the environment at call time, never stored."""

import os

from google import genai

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=api_key)
