import json
import os
from typing import Any

from dotenv import load_dotenv


load_dotenv()


def get_llm_mode() -> str:
    """
    Read LLM mode from environment.

    Supported modes:
    - mock: local simulated response, no API key required
    - api: real LLM API call
    """

    return os.getenv("LLM_MODE", "mock").strip().lower()


def build_mock_response(prompt: str) -> dict[str, Any]:
    """
    Return a deterministic mock response for local development.

    This allows the RAG pipeline to be tested without using a paid API.
    """

    return {
        "answer": (
            "Based on the retrieved knowledge base, InsightFlow AI can support the client's "
            "pre-sales question, but the final response should be reviewed by a human solution "
            "consultant before being sent externally."
        ),
        "sources": [],
        "confidence": "medium",
        "missing_info": [
            "Client's current system architecture",
            "Deployment preference",
            "Security and compliance requirements",
        ],
        "suggested_follow_up": (
            "Could you share your current data sources, BI tools, and deployment requirements "
            "so we can confirm the best implementation approach?"
        ),
        "llm_mode": "mock",
    }


def call_llm_api(prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
    """
    Call a real LLM API using the OpenAI Python SDK.

    This function is designed to be provider-switchable later through:
    - LLM_PROVIDER
    - LLM_MODEL
    - OPENAI_BASE_URL
    - OPENAI_API_KEY
    """

    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-5.5")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Please create a .env file or use LLM_MODE=mock."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "answer": content,
            "sources": [],
            "confidence": "unknown",
            "missing_info": [],
            "suggested_follow_up": "",
            "llm_mode": "api",
        }

    parsed["llm_mode"] = "api"
    return parsed


def call_llm(prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
    """
    Unified LLM entry point.

    The rest of the RAG project should call this function instead of calling
    a specific model provider directly.
    """

    mode = get_llm_mode()

    if mode == "mock":
        return build_mock_response(prompt)

    if mode == "api":
        return call_llm_api(prompt=prompt, system_prompt=system_prompt)

    raise ValueError(f"Unsupported LLM_MODE: {mode}")