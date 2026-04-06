import os

from openai import AsyncOpenAI


def create_openai_client() -> AsyncOpenAI:
    """Create an AsyncOpenAI client from the OPENAI_API_KEY environment variable.

    Raises ValueError if the key is not set or empty.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Copy backend/.env.example to backend/.env and add your key."
        )
    return AsyncOpenAI(api_key=api_key)
