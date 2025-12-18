from __future__ import annotations

from typing import Any, Dict, List

from packages.github_client.client import GitHubClient
from packages.agents.finder import RepoFinderAgent
from packages.agents.analyst import RepoAnalystAgent
from packages.agents.stack import TechStackAgent
from packages.agents.contrib import ContributionAgent
from packages.agents.improve import ImprovementAdvisorAgent


class Coordinator:
    def __init__(self) -> None:
        gh = GitHubClient()
        self.finder = RepoFinderAgent(gh)
        self.analyst = RepoAnalystAgent(gh)
        self.stack = TechStackAgent(gh)
        self.contrib = ContributionAgent(gh)
        self.improve = ImprovementAdvisorAgent(gh)

    def run(self, query: str, top_n: int = 10, analyze_n: int = 3) -> Dict[str, Any]:
        repos = self.finder.find(query=query, top_n=top_n)
        analyze_n = min(analyze_n, len(repos))

        analyzed: List[Dict[str, Any]] = []
        for c in repos[:analyze_n]:
            full_name = c.repo.full_name
            analyzed.append(
                {
                    "repo": c.model_dump(),
                    "analysis": self.analyst.analyze(full_name).model_dump(),
                    "stack": self.stack.detect(full_name).model_dump(),
                    "contrib": self.contrib.find_issues(full_name).model_dump(),
                    "improve": self.improve.suggest(full_name).model_dump(),
                }
            )

        return {
            "query": query,
            "top": [c.model_dump() for c in repos],
            "analyzed": analyzed,
        }
