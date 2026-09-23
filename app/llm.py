import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMConfigurationError(RuntimeError):
    pass


class LLMProvider:
    provider = "abstract"
    model = "abstract"

    def complete(self, system, user):
        raise NotImplementedError


class HTTPChatProvider(LLMProvider):
    """OpenAI-compatible or Anthropic chat provider using the standard library."""

    def __init__(self, provider, model, api_key, base_url, temperature=0.2, max_tokens=1200):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, system, user):
        if self.provider == "anthropic":
            payload = {"model": self.model, "max_tokens": self.max_tokens,
                       "temperature": self.temperature,
                       "system": system, "messages": [{"role": "user", "content": user}]}
            headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        else:
            payload = {"model": self.model, "temperature": self.temperature,
                       "max_tokens": self.max_tokens,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}
            headers = {"Authorization": f"Bearer {self.api_key}"}
        request = Request(self.base_url, data=json.dumps(payload).encode(), method="POST",
                          headers={**headers, "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode())
        except (HTTPError, URLError, TimeoutError) as error:
            raise RuntimeError(f"LLM request failed for provider {self.provider}: {error}") from error
        if self.provider == "anthropic":
            content = body.get("content", [{}])[0].get("text")
        else:
            content = body.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError(f"LLM provider {self.provider} returned no text")
        return content


def build_llm_provider(environ=None):
    environ = os.environ if environ is None else environ
    provider = environ.get("RESEARCH_LLM_PROVIDER", "").strip().lower()
    if not provider:
        raise LLMConfigurationError(
            "Missing LLM configuration: set RESEARCH_LLM_PROVIDER and "
            "RESEARCH_LLM_API_KEY before running --autonomous."
        )
    if provider not in {"openai", "openai-compatible", "anthropic"}:
        raise LLMConfigurationError(f"Unsupported RESEARCH_LLM_PROVIDER: {provider}")
    api_key = environ.get("RESEARCH_LLM_API_KEY", "").strip()
    if not api_key:
        raise LLMConfigurationError("Missing LLM configuration: set RESEARCH_LLM_API_KEY.")
    default_url = "https://api.anthropic.com/v1/messages" if provider == "anthropic" else \
        "https://api.openai.com/v1/chat/completions"
    return HTTPChatProvider(
        provider=provider,
        model=environ.get("RESEARCH_LLM_MODEL", "claude-3-5-sonnet-latest" if provider == "anthropic" else "gpt-4o-mini"),
        api_key=api_key,
        base_url=environ.get("RESEARCH_LLM_BASE_URL", default_url),
        temperature=float(environ.get("RESEARCH_LLM_TEMPERATURE", "0.2")),
        max_tokens=int(environ.get("RESEARCH_LLM_MAX_TOKENS", "1200")),
    )