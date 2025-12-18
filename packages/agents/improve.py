from __future__ import annotations

from packages.github_client.client import GitHubClient
from packages.models.schemas import ImprovementReport


class ImprovementAdvisorAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh

    def suggest(self, full_name: str) -> ImprovementReport:
        quick_wins = []
        evidence = []

        def missing_file(path: str) -> bool:
            txt = self.gh.get_file_text(full_name, path)
            return txt is None

        if missing_file("CONTRIBUTING.md"):
            quick_wins.append("Add CONTRIBUTING.md with setup steps, dev workflow, and PR guidelines.")
            evidence.append("CONTRIBUTING.md not found at repo root.")

        if missing_file("SECURITY.md"):
            quick_wins.append("Add SECURITY.md with vulnerability reporting process and supported versions.")
            evidence.append("SECURITY.md not found at repo root.")

        if missing_file("LICENSE"):
            quick_wins.append("Add a LICENSE file to clarify usage and contributions.")
            evidence.append("LICENSE not found at repo root.")

        # Basic CI presence check (heuristic)
        has_actions = (
            self.gh.get_file_text(full_name, ".github/workflows/ci.yml") is not None
            or self.gh.get_file_text(full_name, ".github/workflows/main.yml") is not None
        )
        if not has_actions:
            quick_wins.append("Add GitHub Actions CI to run tests/lint on every PR.")
            evidence.append("No common GitHub Actions workflow file found in .github/workflows (ci.yml/main.yml).")

        if missing_file("Dockerfile"):
            quick_wins.append("Add a Dockerfile for consistent local dev and easier onboarding.")
            evidence.append("Dockerfile not found at repo root.")

        return ImprovementReport(quick_wins=quick_wins, evidence=evidence)
