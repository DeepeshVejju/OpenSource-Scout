from __future__ import annotations

from typing import List

from packages.github_client.client import GitHubClient
from packages.models.schemas import RepoCandidate, RepoRef, RepoStats
from packages.scoring.rank import score_repo, rank_repos


class RepoFinderAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh

    def find(self, query: str, top_n: int = 10) -> List[RepoCandidate]:
        items = self.gh.search_repositories(query=query, top_n=top_n)

        candidates: List[RepoCandidate] = []
        for item in items:
            full_name = item["full_name"]
            ref = RepoRef(
                owner=item["owner"]["login"],
                name=item["name"],
                full_name=full_name,
                url=item["html_url"],
            )

            # pull richer stats from /repos/{full_name}
            stats: RepoStats = self.gh.get_repo(full_name)

            score, reasons = score_repo(stats)
            candidates.append(
                RepoCandidate(repo=ref, stats=stats, score=score, reasons=reasons)
            )

        return rank_repos(candidates)
