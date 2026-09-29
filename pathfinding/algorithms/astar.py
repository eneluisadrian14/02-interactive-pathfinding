"""A* Search with admissible Euclidean heuristic."""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from pathfinding.core.graph import MapGraph
from pathfinding.core.heuristics import euclidean_heuristic
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


def a_star_search(graph: MapGraph, start: str, goal: str) -> SearchResult:
    t0 = time.perf_counter()
    if start not in graph.positions or goal not in graph.positions:
        return SearchResult([], float("inf"), 0, 0.0, set(), set(), False)

    h0 = euclidean_heuristic(start, goal, graph.positions)
    root = Node(f_cost=h0, state=start, g_cost=0.0, h_cost=h0, depth=0)

    open_heap: List[Node] = [root]
    g_best: Dict[str, float] = {start: 0.0}
    explored: Set[str] = set()
    in_frontier: Set[str] = {start}
    nodes_expanded = 0

    while open_heap:
        current = heapq.heappop(open_heap)
        in_frontier.discard(current.state)

        if current.state in explored:
            continue
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
                frontier_final=set(in_frontier),
                found=True,
            )

        for neigh, edge_cost in graph.neighbors(current.state).items():
            tentative_g = current.g_cost + edge_cost
            if neigh in g_best and tentative_g >= g_best[neigh]:
                continue
            g_best[neigh] = tentative_g
            h = euclidean_heuristic(neigh, goal, graph.positions)
            child = Node(
                f_cost=tentative_g + h,
                state=neigh,
                parent=current,
                g_cost=tentative_g,
                h_cost=h,
                depth=current.depth + 1,
            )
            heapq.heappush(open_heap, child)
            in_frontier.add(neigh)

    elapsed = time.perf_counter() - t0
    return SearchResult([], float("inf"), nodes_expanded, elapsed, explored, set(), False)
