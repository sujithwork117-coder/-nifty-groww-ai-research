import json

import pytest

from app.llm import LLMConfigurationError, build_llm_provider


def test_llm_provider_requires_explicit_configuration():
    with pytest.raises(LLMConfigurationError, match="RESEARCH_LLM_PROVIDER"):
        build_llm_provider({})


def test_llm_provider_reads_model_and_generation_settings():
    provider = build_llm_provider({
        "RESEARCH_LLM_PROVIDER": "openai-compatible",
        "RESEARCH_LLM_API_KEY": "test-only",
        "RESEARCH_LLM_MODEL": "local-model",
        "RESEARCH_LLM_BASE_URL": "http://localhost:9999/chat",
        "RESEARCH_LLM_TEMPERATURE": "0.4",
        "RESEARCH_LLM_MAX_TOKENS": "321",
    })

    assert provider.model == "local-model"
    assert provider.temperature == 0.4
    assert provider.max_tokens == 321
    assert provider.api_key == "test-only"


def test_llm_provider_accepts_groq_alias():
    provider = build_llm_provider({
        "RESEARCH_LLM_PROVIDER": "groq",
        "RESEARCH_LLM_API_KEY": "test-only",
        "RESEARCH_LLM_MODEL": "openai/gpt-oss-20b",
        "RESEARCH_LLM_BASE_URL": "https://api.groq.com/openai/v1/chat/completions",
    })

    assert provider.provider == "groq"
    assert provider.model == "openai/gpt-oss-20b"
    assert provider.base_url == "https://api.groq.com/openai/v1/chat/completions"