from __future__ import annotations

from typing import List

from packages.github_client.client import GitHubClient
from packages.models.schemas import TechStackReport


def _add_unique(lst: List[str], item: str) -> None:
    if item not in lst:
        lst.append(item)


class TechStackAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh

    def detect(self, full_name: str) -> TechStackReport:
        languages = self.gh.get_languages(full_name)

        frameworks: List[str] = []
        tools: List[str] = []
        infra: List[str] = []

        pom = self.gh.get_file_text(full_name, "pom.xml")
        if pom:
            if "spring-boot-starter" in pom:
                _add_unique(frameworks, "Spring Boot")
            _add_unique(tools, "Maven")

        gradle = self.gh.get_file_text(full_name, "build.gradle")
        if gradle:
            if "org.springframework.boot" in gradle:
                _add_unique(frameworks, "Spring Boot")
            _add_unique(tools, "Gradle")

        pkg = self.gh.get_file_text(full_name, "package.json")
        if pkg:
            if '"react"' in pkg or "'react'" in pkg:
                _add_unique(frameworks, "React")
            if '"next"' in pkg or '"nextjs"' in pkg:
                _add_unique(frameworks, "Next.js")
            if '"express"' in pkg:
                _add_unique(frameworks, "Express")
            _add_unique(tools, "Node.js")

        req = self.gh.get_file_text(full_name, "requirements.txt")
        if req:
            if "fastapi" in req.lower():
                _add_unique(frameworks, "FastAPI")
            if "django" in req.lower():
                _add_unique(frameworks, "Django")
            _add_unique(tools, "pip")

        pyproject = self.gh.get_file_text(full_name, "pyproject.toml")
        if pyproject:
            low = pyproject.lower()
            if "poetry" in low:
                _add_unique(tools, "Poetry")
            if "fastapi" in low:
                _add_unique(frameworks, "FastAPI")

        dockerfile = self.gh.get_file_text(full_name, "Dockerfile")
        if dockerfile:
            _add_unique(infra, "Docker")

        compose = self.gh.get_file_text(full_name, "docker-compose.yml")
        if compose:
            _add_unique(infra, "docker-compose")

        # GitHub Actions heuristic: check if folder exists by trying a common workflow file
        ci = self.gh.get_file_text(full_name, ".github/workflows/ci.yml")
        if ci or self.gh.get_file_text(full_name, ".github/workflows/main.yml"):
            _add_unique(infra, "GitHub Actions")

        return TechStackReport(
            languages=languages,
            frameworks=frameworks,
            tools=tools,
            infra_signals=infra,
        )
