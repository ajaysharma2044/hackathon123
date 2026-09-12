"""
Investor / fund graph from PUBLIC data only (docs/venture/fund-graph.md; Parts XXXII, LVIII).

Structural fund + investor records built from public fund websites, announcements, portfolios, and
public professional profiles. No private or scraped contact data.
"""
from __future__ import annotations
from dataclasses import dataclass, field

STAGES = ("PRE_SEED", "SEED", "SERIES_A", "SERIES_B", "GROWTH")
INVESTOR_ROLES = ("GP", "PARTNER", "PRINCIPAL", "ASSOCIATE", "PLATFORM", "SCOUT")


@dataclass
class Fund:
    fund_id: str
    name: str
    stage: str = "SEED"
    check_size: str = ""
    sectors: tuple = ()
    geography: str = ""
    thesis: str = ""
    source_url: str = ""          # public source, required for any real fund row

    def __post_init__(self):
        if self.stage not in STAGES:
            raise ValueError(f"unknown stage {self.stage!r}")


@dataclass
class Investor:
    investor_id: str
    fund_id: str
    name: str = ""
    role: str = "ASSOCIATE"
    public_profile_url: str = ""

    def __post_init__(self):
        if self.role not in INVESTOR_ROLES:
            raise ValueError(f"unknown investor role {self.role!r}")


def funds_in_sector(funds, sector: str) -> list:
    return [f for f in funds if sector in f.sectors]


def funds_at_stage(funds, stage: str) -> list:
    return [f for f in funds if f.stage == stage]
