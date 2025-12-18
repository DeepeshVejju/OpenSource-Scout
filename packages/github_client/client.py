from __future__ import annotations

import os
import base64
from typing import List, Dict, Optional

import httpx
from dotenv import load_dotenv

from packages.models.schemas import RepoRef, RepoStats

load_dotenv()

GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")


class GitHubClient:
    def __init__(self) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
        }
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"

        self.client = httpx.Client(base_url=GITHUB_API, headers=headers, timeout=30.0)

    def search_repositories(self, query: str, top_n: int = 10) -> List[Dict]:
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(top_n, 50),
        }
        r = self.client.get("/search/repositories", params=params)
        r.raise_for_status()
        return r.json().get("items", [])

    def get_repo(self, full_name: str) -> RepoStats:
        r = self.client.get(f"/repos/{full_name}")
        r.raise_for_status()
        data = r.json()

        return RepoStats(
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            pushed_at=data.get("pushed_at"),
            description=data.get("description"),
            topics=data.get("topics", []),
            license=(data.get("license") or {}).get("name"),
        )

    def get_languages(self, full_name: str) -> Dict[str, int]:
        r = self.client.get(f"/repos/{full_name}/languages")
        r.raise_for_status()
        return r.json()

    def get_readme(self, full_name: str) -> Optional[str]:
        r = self.client.get(f"/repos/{full_name}/readme")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        content = data.get("content")
        if not content:
            return None
        return base64.b64decode(content).decode("utf-8", errors="ignore")

    def get_file_text(self, full_name: str, path: str) -> Optional[str]:
        r = self.client.get(f"/repos/{full_name}/contents/{path}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        content = data.get("content")
        if not content:
            return None
        return base64.b64decode(content).decode("utf-8", errors="ignore")

    def list_issues(
        self,
        full_name: str,
        labels: List[str],
        top_n: int = 10,
    ) -> List[Dict]:
        params = {
            "state": "open",
            "labels": ",".join(labels),
            "per_page": min(top_n, 50),
        }
        r = self.client.get(f"/repos/{full_name}/issues", params=params)
        r.raise_for_status()
        return r.json()
