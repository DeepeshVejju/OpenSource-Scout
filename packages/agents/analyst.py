from __future__ import annotations

import re
from typing import Optional

from packages.github_client.client import GitHubClient
from packages.models.schemas import RepoAnalysis
from packages.llm.client import LLMClient


def _first_nonempty_paragraph(md: str) -> Optional[str]:
    lines = [ln.strip() for ln in md.splitlines()]
    cleaned = []
    for ln in lines:
        if not ln:
            cleaned.append("")
            continue
        if ln.startswith("![") or ln.startswith("[![") or ln.startswith("<img"):
            continue
        cleaned.append(ln)

    text = "\n".join(cleaned).strip()
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return parts[0] if parts else None


def _extract_section(md: str, names: list[str]) -> Optional[str]:
    pattern = r"(?im)^(#{1,6})\s*(" + "|".join(map(re.escape, names)) + r")\s*$"
    m = re.search(pattern, md)
    if not m:
        return None

    start = m.end()
    m2 = re.search(r"(?im)^#{1,6}\s+.+$", md[start:])
    end = start + (m2.start() if m2 else len(md[start:]))
    section = md[start:end].strip()
    return section if section else None


class RepoAnalystAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh
        self.llm = LLMClient()

    def analyze(self, full_name: str) -> RepoAnalysis:
        readme = self.gh.get_readme(full_name) or ""

        # LLM-powered grounded summary
        llm_summary = self.llm.summarize_repo_readme(readme)

        # Deterministic "how to run"
        install = _extract_section(readme, ["Installation", "Install", "Setup"])
        usage = _extract_section(readme, ["Usage", "Quickstart", "Getting Started", "Run"])
        how_to_run = "\n\n".join(p for p in [install, usage] if p) or None

        return RepoAnalysis(
            summary=llm_summary,
            how_to_run=how_to_run,
            key_links=[f"https://github.com/{full_name}"],
        )
