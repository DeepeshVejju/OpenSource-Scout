from __future__ import annotations

from packages.github_client.client import GitHubClient
from packages.models.schemas import ImprovementReport


class ImprovementAdvisorAgent:
    def __init__(self, gh: GitHubClient) -> None:
        self.gh = gh

    def _dir_filenames(self, full_name: str, path: str) -> set[str]:
        items = self.gh.list_dir(full_name, path)
        return {it.get("name", "").lower() for it in items if it.get("type") == "file"}

    def suggest(self, full_name: str) -> ImprovementReport:
        quick_wins: list[str] = []
        evidence: list[str] = []

        # Directory listings are reliable and cheap
        root_files = self._dir_filenames(full_name, "")
        gh_files = self._dir_filenames(full_name, ".github")
        docs_files = self._dir_filenames(full_name, "docs")

        def found_in_common_places(candidates: list[str]) -> str | None:
            for name in candidates:
                n = name.lower()
                if n in root_files:
                    return f"/{name}"
                if n in gh_files:
                    return f".github/{name}"
                if n in docs_files:
                    return f"docs/{name}"
            return None

        # CONTRIBUTING: "common places" check; otherwise mark unknown instead of claiming missing
        contrib_path = found_in_common_places(
            ["CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt", "CONTRIBUTING.mdx"]
        )
        if contrib_path:
            evidence.append(f"Contributing guide detected at: {contrib_path}")
        else:
            evidence.append("Contributing guide not found in root/.github/docs (may exist deeper or in website docs).")
            quick_wins.append("Consider adding a clear CONTRIBUTING guide in root or .github for easier onboarding.")

        # SECURITY: same approach
        sec_path = found_in_common_places(
            ["SECURITY.md", "SECURITY.rst", "SECURITY.txt", "SECURITY-POLICY.md", "SECURITYPOLICY.md"]
        )
        if sec_path:
            evidence.append(f"Security policy detected at: {sec_path}")
        else:
            evidence.append("Security policy not found in root/.github/docs (may exist elsewhere).")
            quick_wins.append("Consider adding SECURITY.md in .github/ to document vulnerability reporting.")

        # LICENSE: usually root; here we can be stricter
        lic_path = found_in_common_places(["LICENSE", "LICENSE.md", "LICENSE.txt"])
        if lic_path:
            evidence.append(f"License detected at: {lic_path}")
        else:
            evidence.append("License not found in root/.github/docs.")
            quick_wins.append("Add a LICENSE file at repo root to clarify usage and contributions.")

        # CI workflows: directory presence is reliable
        workflows = self.gh.list_dir(full_name, ".github/workflows")
        if any(it.get("type") == "file" for it in workflows):
            evidence.append("GitHub Actions workflows detected under .github/workflows.")
        else:
            evidence.append("No files found under .github/workflows.")
            quick_wins.append("Add GitHub Actions workflows under .github/workflows to run tests/lint on PRs.")

        # Docker support (root): safe claim
        dockerfile = self.gh.get_file_text(full_name, "Dockerfile")
        compose_yml = self.gh.get_file_text(full_name, "docker-compose.yml")
        compose_yaml = self.gh.get_file_text(full_name, "docker-compose.yaml")
        if dockerfile or compose_yml or compose_yaml:
            evidence.append("Docker support detected at repo root (Dockerfile and/or docker-compose present).")
        else:
            evidence.append("No Dockerfile or docker-compose.yml/.yaml found at repo root.")
            quick_wins.append("Consider adding Dockerfile/docker-compose for consistent local dev (if appropriate).")

        return ImprovementReport(quick_wins=quick_wins, evidence=evidence)
