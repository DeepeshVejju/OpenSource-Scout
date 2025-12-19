from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMClient:
    """
    Minimal OpenAI chat client wrapper.
    Requires: OPENAI_API_KEY in your .env
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def summarize_repo_readme(self, readme_text: str, max_chars: int = 8000) -> str:
        text = (readme_text or "").strip()
        if not text:
            return "README not found or empty."

        # Keep request bounded
        text = text[:max_chars]

        prompt = (
            "You are analyzing a GitHub repository README.\n"
            "Task:\n"
            "1) Write a 3-5 sentence summary of what the project does.\n"
            "2) Add one line: 'Best for:' describing the target user.\n"
            "Rules:\n"
            "- Use only information present in the README.\n"
            "- If info is missing, say 'Not specified'.\n"
            "- Do NOT invent features.\n\n"
            "README:\n"
            f"{text}"
        )

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        return (resp.choices[0].message.content or "").strip()
    
    
