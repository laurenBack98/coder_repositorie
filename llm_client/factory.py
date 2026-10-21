try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover - optional dependency
    ChatGroq = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None

try:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
except ImportError:  # pragma: no cover - optional dependency
    ChatHuggingFace = None
    HuggingFaceEndpoint = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:  # pragma: no cover - optional dependency
    ChatAnthropic = None

from .schemas import Provider, LLMConfig


def _require_dependency(provider_name: str, module_name: str, cls):
    if cls is None:
        raise ImportError(
            f"Falta la dependencia '{module_name}' para usar el proveedor '{provider_name}'. "
            f"Instalá: pip install {module_name}"
        )
    return cls


def build_llm_client(config: LLMConfig):
    """Factory para instanciar el cliente adecuado según el proveedor."""
    secret_key = config.api_key.get_secret_value() if config.api_key else None

    if config.provider == Provider.OPENAI:
        ChatOpenAI_cls = _require_dependency("openai", "langchain-openai", ChatOpenAI)
        kwargs = {"model": config.model, "temperature": config.temperature}
        if secret_key:
            kwargs["api_key"] = secret_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatOpenAI_cls(**kwargs)

    if config.provider == Provider.ANTHROPIC:
        ChatAnthropic_cls = _require_dependency("anthropic", "langchain-anthropic", ChatAnthropic)
        kwargs = {"model": config.model, "temperature": config.temperature}
        if secret_key:
            kwargs["api_key"] = secret_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatAnthropic_cls(**kwargs)

    if config.provider == Provider.GROQ:
        ChatGroq_cls = _require_dependency("groq", "langchain-groq", ChatGroq)
        kwargs = {"model": config.model, "temperature": config.temperature}
        if secret_key:
            kwargs["api_key"] = secret_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatGroq_cls(**kwargs)

    if config.provider == Provider.GEMINI:
        ChatGoogleGenerativeAI_cls = _require_dependency(
            "gemini", "langchain-google-genai", ChatGoogleGenerativeAI
        )
        kwargs = {"model": config.model, "temperature": config.temperature}
        if secret_key:
            kwargs["google_api_key"] = secret_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return ChatGoogleGenerativeAI_cls(**kwargs)

    if config.provider == Provider.HUGGINGFACE:
        ChatHuggingFace_cls = _require_dependency(
            "huggingface", "langchain-huggingface", ChatHuggingFace
        )
        HuggingFaceEndpoint_cls = _require_dependency(
            "huggingface", "langchain-huggingface", HuggingFaceEndpoint
        )
        endpoint_kwargs = {
            "repo_id": config.model,
            "temperature": config.temperature if config.temperature > 0 else 0.01,
            "task": "text-generation",
        }
        if secret_key:
            endpoint_kwargs["huggingfacehub_api_token"] = secret_key
        if config.base_url:
            endpoint_kwargs["endpoint_url"] = config.base_url

        endpoint = HuggingFaceEndpoint_cls(**endpoint_kwargs)
        return ChatHuggingFace_cls(llm=endpoint)

    if config.provider == Provider.DEEPSEEK:
        ChatOpenAI_cls = _require_dependency("deepseek", "langchain-openai", ChatOpenAI)
        kwargs = {"model": config.model, "temperature": config.temperature}
        if secret_key:
            kwargs["api_key"] = secret_key
        kwargs["base_url"] = config.base_url or "https://api.deepseek.com/v1"
        return ChatOpenAI_cls(**kwargs)

    raise ValueError(f"Proveedor desconocido: {config.provider}")