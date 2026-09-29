"""Breadth-First Search (uninformed)."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from pathfinding.core.graph import MapGraph
from pathfinding.core.node import Node


@dataclass
class SearchResult:
    path: List[str]
    cost: float
    nodes_expanded: int
    elapsed_sec: float
    explored: Set[str]
    frontier_final: Set[str]
    found: bool


def bfs_search(graph: MapGraph, start: str, goal: str) -> SearchResult:
    t0 = time.perf_counter()
    if start not in graph.positions or goal not in graph.positions:
        return SearchResult([], float("inf"), 0, 0.0, set(), set(), False)

    root = Node(f_cost=0.0, state=start, g_cost=0.0, h_cost=0.0, depth=0)
    queue: deque[Node] = deque([root])
    visited: Set[str] = {start}
    explored: Set[str] = set()
    nodes_expanded = 0
    came: Dict[str, Node] = {start: root}

    while queue:
        current = queue.popleft()
        explored.add(current.state)
        nodes_expanded += 1

        if current.state == goal:
            elapsed = time.perf_counter() - t0
            return SearchResult(
                path=current.path(),
                cost=current.g_cost,
                nodes_expanded=nodes_expanded,
                elapsed_sec=elapsed,
                explored=explored,
                frontier_final={n.state for n in queue},
                found=True,
            )

        for neigh, edge_cost in graph.neighbors(current.state).items():
            if neigh in visited:
                continue
            visited.add(neigh)
            child = Node(
                f_cost=current.g_cost + edge_cost,
                state=neigh,
                parent=current,
                g_cost=current.g_cost + edge_cost,
                h_cost=0.0,
                depth=current.depth + 1,
            )
            came[neigh] = child
            queue.append(child)

    elapsed = time.perf_counter() - t0
    return SearchResult([], float("inf"), nodes_expanded, elapsed, explored, set(), False)
