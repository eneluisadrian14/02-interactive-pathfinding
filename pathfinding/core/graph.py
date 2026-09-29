"""Graph loading and topology helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


Coord = Tuple[float, float]
AdjList = Dict[str, Dict[str, float]]


@dataclass
class MapGraph:
    positions: Dict[str, Coord]
    edges: AdjList
    default_start: str | None = None
    default_goal: str | None = None

    @property
    def nodes(self) -> List[str]:
        return list(self.positions.keys())

    def neighbors(self, state: str) -> Dict[str, float]:
        return self.edges.get(state, {})

    @classmethod
    def from_json(cls, path: str | Path) -> "MapGraph":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        positions = {name: (float(xy[0]), float(xy[1])) for name, xy in data["positions"].items()}
        edges: AdjList = {name: {} for name in positions}
        for u, v, cost in data["edges"]:
            if u in edges and v in edges:
                edges[u][v] = float(cost)
                edges[v][u] = float(cost)

        return cls(
            positions=positions,
            edges=edges,
            default_start=data.get("start"),
            default_goal=data.get("goal"),
        )
