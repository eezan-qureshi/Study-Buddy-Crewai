"""Custom tools (Part 4 of the course). The agent decides WHEN to call them."""
import json, urllib.parse, urllib.request
from crewai.tools import tool


@tool("Wikipedia summary")
def wikipedia_summary(topic: str) -> str:
    """Get a short factual summary of a topic from Wikipedia. Input: the topic name, e.g. 'Machine learning'."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(topic.strip().replace(" ", "_"))
    req = urllib.request.Request(url, headers={"User-Agent": "StudyBuddy/1.0 (student project)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("extract") or "No summary found for this topic."
    except Exception as e:  # no internet / page not found
        return f"Wikipedia not available ({type(e).__name__}). Use your own knowledge and say so."


@tool("Word count")
def word_count(text: str) -> str:
    """Count how many words are in a text. Input: the text."""
    return str(len(text.split()))
