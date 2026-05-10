"""Groq LLM wrapper with retries and JSON-mode structured output."""
import os
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import Type, TypeVar

T = TypeVar("T", bound=BaseModel)

def get_llm(temperature: float = 0.7) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in .env file for local development or in Streamlit Cloud secrets."
        )
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=temperature,
        max_retries=3,
    )

def structured_call(prompt: str, schema: Type[T], temperature: float = 0.4) -> T:
    """Call LLM with a Pydantic schema. Retries once on parse failure."""
    llm = get_llm(temperature=temperature).with_structured_output(schema, method="json_mode")
    try:
        return llm.invoke(prompt)
    except Exception as e:
        # Retry once with a stricter reminder
        return llm.invoke(prompt + "\n\nReturn ONLY valid JSON matching the schema. No prose.")
