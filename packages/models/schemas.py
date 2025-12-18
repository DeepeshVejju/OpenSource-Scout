from __future__ import annotations

from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class RepoRef(BaseModel):
    owner: str
    name: str
    full_name: str
    url: str


class RepoStats(BaseModel):
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    pushed_at: Optional[str] = None  # ISO string for now
    description: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    license: Optional[str] = None


class RepoCandidate(BaseModel):
    repo: RepoRef
    stats: RepoStats
    score: float = 0.0
    reasons: List[str] = Field(default_factory=list)


class RepoAnalysis(BaseModel):
    summary: Optional[str] = None
    how_to_run: Optional[str] = None
    key_links: List[str] = Field(default_factory=list)


class TechStackReport(BaseModel):
    languages: Dict[str, int] = Field(default_factory=dict)  # language -> bytes
    frameworks: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    infra_signals: List[str] = Field(default_factory=list)


class ContributionIssue(BaseModel):
    title: str
    url: str
    labels: List[str] = Field(default_factory=list)
    updated_at: Optional[str] = None  # ISO string


class ContributionReport(BaseModel):
    issues: List[ContributionIssue] = Field(default_factory=list)


class ImprovementReport(BaseModel):
    quick_wins: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
