"""Shared setup (same idea as the teacher's config.py).
get_llm() builds the Groq LLM. The key comes from the .env file or from the Streamlit sidebar."""
import os, sys, logging
from dotenv import load_dotenv

load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"          # no telemetry
os.environ["CREWAI_TRACING_ENABLED"] = "false"    # no "view tracing?" question

try:  # Windows console: allow emoji and symbols
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# llama-3.3-70b-versatile was retired by Groq on 16 Aug 2026; gpt-oss-120b is the recommended replacement.
# You can change the model without editing code: add  GROQ_MODEL=...  to the .env file.
MODEL = "openai/" + os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def get_api_key(key=None):
    key = key or os.getenv("GROQ_API_KEY")
    if not key or key == "paste_your_key_here":
        raise ValueError("GROQ_API_KEY not found. Put it in the .env file or paste it in the sidebar.")
    return key


def get_llm(key=None):
    from crewai import LLM
    logging.getLogger("crewai.llms.base_llm").setLevel(logging.ERROR)
    # Groq speaks the OpenAI protocol, so we use the "openai/" connector and point it to Groq.
    return LLM(
        model=MODEL,
        base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=get_api_key(key),
        temperature=0.2,
    )