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
    
    def list_dir(self, full_name: str, path: str) -> list[dict]:
        """
        List directory contents (files/folders) at a given path.
        Returns [] if path doesn't exist or isn't a directory.
        """
        r = self.client.get(f"/repos/{full_name}/contents/{path}")
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []

    def list_repo_paths(self, full_name: str) -> list[str]:
        """
        Returns a list of all file paths in the repo (recursive) using the git tree API.
        Correctly resolves the default branch -> commit SHA -> tree SHA.
        """
        # Get default branch
        r = self.client.get(f"/repos/{full_name}")
        r.raise_for_status()
        repo = r.json()
        branch = repo.get("default_branch", "main")

        # Get branch ref -> commit SHA
        r2 = self.client.get(f"/repos/{full_name}/git/ref/heads/{branch}")
        r2.raise_for_status()
        ref = r2.json()
        commit_sha = ref["object"]["sha"]

        # Get commit -> tree SHA
        r3 = self.client.get(f"/repos/{full_name}/git/commits/{commit_sha}")
        r3.raise_for_status()
        commit = r3.json()
        tree_sha = commit["tree"]["sha"]

        # List tree recursively
        r4 = self.client.get(f"/repos/{full_name}/git/trees/{tree_sha}", params={"recursive": "1"})
        r4.raise_for_status()
        tree = r4.json().get("tree", [])

        return [
            item["path"]
            for item in tree
            if item.get("type") == "blob" and "path" in item
        ]
    
    def try_get_first_existing_text(self, full_name: str, paths: list[str]) -> tuple[str | None, str | None]:
        """
        Returns (path, text) for the first path that exists and has readable text content.
        If none exist, returns (None, None).
        """
        for p in paths:
            txt = self.get_file_text(full_name, p)
            if txt:
                return p, txt
        return None, None
    
    def search_code(self, query: str, top_n: int = 10) -> list[dict]:
        """
        GitHub code search. Example query:
        'repo:langchain-ai/langchain filename:CONTRIBUTING'
        """
        params = {"q": query, "per_page": min(top_n, 50)}
        r = self.client.get("/search/code", params=params)
        r.raise_for_status()
        return r.json().get("items", [])


