from __future__ import annotations

from typing import List

from packages.github_client.client import GitHubClient
from packages.models.schemas import ContributionIssue, ContributionReport


class ContributionAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh

    def find_issues(self, full_name: str, top_n: int = 10) -> ContributionReport:
        label_sets: List[List[str]] = [
            ["good first issue"],
            ["help wanted"],
            ["documentation"],
        ]

        issues_out: List[ContributionIssue] = []
        seen = set()

        for labels in label_sets:
            issues = self.gh.list_issues(full_name, labels=labels, top_n=top_n)
            for it in issues:
                # skip PRs (GitHub issues API returns PRs too)
                if "pull_request" in it:
                    continue
                url = it.get("html_url")
                if not url or url in seen:
                    continue
                seen.add(url)

                issues_out.append(
                    ContributionIssue(
                        title=it.get("title", "").strip(),
                        url=url,
                        labels=[l["name"] for l in it.get("labels", [])],
                        updated_at=it.get("updated_at"),
                    )
                )

        return ContributionReport(issues=issues_out[:top_n])
