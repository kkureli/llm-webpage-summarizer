"""Summarize a webpage with a local Ollama model."""

from __future__ import annotations

from openai import OpenAI

from scraper import fetch_website_contents

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "llama3.2"

ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

SYSTEM_PROMPT = """
You are an assistant that summarizes the specific webpage content provided.
Focus on the main article or page topic — ignore leftover navigation, menus, or site chrome.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

USER_PROMPT_PREFIX = """
Here is the content of a specific webpage.
Provide a short summary of THIS page (not the whole website).
If it is a news article, summarize the article and any key announcements in it.

"""


def messages_for(website: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_PREFIX + website},
    ]


def summarize(url: str) -> str:
    website = fetch_website_contents(url)
    if not website.strip():
        raise ValueError("No readable text found on the page.")

    response = ollama.chat.completions.create(
        model=MODEL,
        messages=messages_for(website),
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
