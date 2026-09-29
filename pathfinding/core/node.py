"""Search node for state-space exploration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(order=True)
class Node:
    """A* / BFS search node. Ordering uses f_cost for the priority queue."""

    f_cost: float
    state: str = field(compare=False)
    parent: Optional["Node"] = field(default=None, compare=False)
    g_cost: float = field(default=0.0, compare=False)
    h_cost: float = field(default=0.0, compare=False)
    depth: int = field(default=0, compare=False)

    def path(self) -> List[str]:
        nodes: List[str] = []
        cur: Optional[Node] = self
        while cur is not None:
            nodes.append(cur.state)
            cur = cur.parent
        return list(reversed(nodes))
