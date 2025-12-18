from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import List

from packages.models.schemas import RepoCandidate, RepoStats


def _days_since(iso_ts: str | None) -> int | None:
    if not iso_ts:
        return None
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


def score_repo(stats: RepoStats) -> tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    # Stars (log-scaled)
    if stats.stars > 0:
        s = math.log10(stats.stars + 1) * 10
        score += s
        reasons.append(f"{stats.stars} stars")

    # Recency
    days = _days_since(stats.pushed_at)
    if days is not None:
        if days <= 30:
            score += 10
            reasons.append("updated in last 30 days")
        elif days <= 90:
            score += 5
            reasons.append("updated in last 90 days")
        elif days <= 365:
            score += 2
            reasons.append("updated in last year")

    # Community / hygiene signals
    if stats.license:
        score += 2
        reasons.append("has license")

    if stats.topics:
        score += 1
        reasons.append("has topics")

    if stats.description:
        score += 1
        reasons.append("has description")

    # Light penalty for huge issue backlog
    if stats.open_issues > 500:
        score -= 2
        reasons.append("large open issue backlog")

    return round(score, 2), reasons


def rank_repos(candidates: List[RepoCandidate]) -> List[RepoCandidate]:
    return sorted(candidates, key=lambda c: c.score, reverse=True)
