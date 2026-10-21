import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()

SUPPORTED_PROVIDERS = (
    "Gemini",
    "OpenAI",
    "Groq",
    "OpenAI-compatible",
    "Ollama",
)

DEFAULT_MODELS = {
    "Gemini": "gemini-2.5-flash",
    "OpenAI": "gpt-4o-mini",
    "Groq": "llama-3.3-70b-versatile",
    "OpenAI-compatible": "gpt-4o-mini",
    "Ollama": "llama3.2",
}

API_KEY_ENV_VARS = {
    "Gemini": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    "OpenAI": ("OPENAI_API_KEY",),
    "Groq": ("GROQ_API_KEY",),
    "OpenAI-compatible": (
        "OPENAI_COMPATIBLE_API_KEY",
        "OPENROUTER_API_KEY",
    ),
}

MODEL_ENV_VARS = {
    "Gemini": "GEMINI_API_MODEL",
    "OpenAI": "OPENAI_MODEL",
    "Groq": "GROQ_MODEL",
    "OpenAI-compatible": "OPENAI_COMPATIBLE_MODEL",
    "Ollama": "OLLAMA_MODEL",
}

BASE_URL_ENV_VARS = {
    "OpenAI-compatible": ("OPENAI_COMPATIBLE_BASE_URL", "OPENAI_BASE_URL"),
    "Ollama": ("OLLAMA_BASE_URL",),
}


def get_configured_api_key(provider):
    for env_var in API_KEY_ENV_VARS.get(provider, ()):
        api_key = os.getenv(env_var)
        if api_key:
            return api_key
    return ""


def get_default_model(provider):
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unsupported API provider: {provider}")
    return os.getenv(MODEL_ENV_VARS[provider], DEFAULT_MODELS[provider])


def get_default_base_url(provider):
    for env_var in BASE_URL_ENV_VARS.get(provider, ()):
        base_url = os.getenv(env_var)
        if base_url:
            return base_url
    if provider == "Ollama":
        return "http://localhost:11434"
    return ""


def get_model(provider="Gemini", model_name=None, api_key=None, base_url=None):
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported API provider: {provider}")

    model_name = model_name or get_default_model(provider)
    api_key = (api_key or "").strip() or get_configured_api_key(provider)

    if provider == "Ollama":
        return ChatOllama(
            model=model_name,
            base_url=(base_url or "").strip() or get_default_base_url(provider),
        )

    if not api_key:
        env_vars = ", ".join(API_KEY_ENV_VARS[provider])
        raise ValueError(
            f"{provider} API key is missing. Enter it in the sidebar or set "
            f"{env_vars} in your environment."
        )

    if provider == "Gemini":
        return ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
    if provider == "OpenAI":
        return ChatOpenAI(model=model_name, api_key=api_key)
    if provider == "Groq":
        return ChatGroq(model=model_name, api_key=api_key)

    base_url = (base_url or "").strip()
    if not base_url:
        raise ValueError(
            "Enter a base URL for the OpenAI-compatible API in the sidebar."
        )
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
