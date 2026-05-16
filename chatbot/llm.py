import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# Initialize LLM with OpenRouter
llm = ChatOpenAI(
    temperature=0.0,  # Low temperature for more consistent medical advice
    model="mistralai/mistral-large-2512",
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=1024,  # Limit response length
    request_timeout=30
)


class LLMResponse:
    """Simple container to normalize LLM responses to have `.content`."""
    def __init__(self, content: str):
        self.content = content


def invoke(prompt: str):
    """Invoke the configured `llm` with a prompt and return an object with `.content`.

    This wrapper is defensive: different LLM clients expose different call
    signatures (`__call__`, `generate`, `invoke`, etc.). We try common
    methods and normalize the output.
    """
    # Try common LangChain-style method names
    try:
        # Some integrations provide `invoke(prompt)` returning a response-like object
        resp = llm.invoke(prompt)
    except Exception:
        try:
            # Many LangChain LLMs are callable: `llm(prompt)` returning a message-like object
            resp = llm(prompt)
        except Exception:
            try:
                # Older API: generate -> returns a Generation object
                gen = llm.generate([prompt])
                # Attempt to extract text from common fields
                if hasattr(gen, 'generations') and gen.generations:
                    text = gen.generations[0][0].text
                    return LLMResponse(text)
                resp = gen
            except Exception as e:
                raise RuntimeError(f"LLM invocation failed: {e}")

    # Normalize response to have `.content` string
    # If resp has `.content`, use it; otherwise extract likely fields.
    if hasattr(resp, 'content') and isinstance(resp.content, str):
        return resp

    # Some clients return a simple string
    if isinstance(resp, str):
        return LLMResponse(resp)

    # LangChain Chat models often return a BaseMessage or dict-like
    # Try to extract a textual field
    text = None
    if hasattr(resp, 'generations'):
        try:
            text = resp.generations[0][0].text
        except Exception:
            pass

    if text is None and hasattr(resp, 'text'):
        text = resp.text

    if text is None and isinstance(resp, dict):
        # try common dict keys
        for k in ('content', 'text', 'message'):
            if k in resp and isinstance(resp[k], str):
                text = resp[k]
                break

    if text is None:
        # Fallback to string representation
        text = str(resp)

    return LLMResponse(text)