"""One-off check that GEMINI_API_KEY works: python -m scripts.gemini_smoke (from backend/)."""

import os
import sys

from app.llm import DEFAULT_MODEL, get_client


def main() -> int:
    print(f"GEMINI_API_KEY length: {len(os.environ.get('GEMINI_API_KEY', ''))}")
    client = get_client()
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents="Reply with exactly the word: pong",
    )
    print(f"model: {DEFAULT_MODEL}")
    print(f"response: {response.text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
