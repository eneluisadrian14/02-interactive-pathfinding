"""Admissible heuristics for A*."""

from __future__ import annotations

import math
from typing import Dict, Tuple


def euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def euclidean_heuristic(
    state: str,
    goal: str,
    positions: Dict[str, Tuple[float, float]],
) -> float:
    """
    Straight-line distance — admissible when edge costs are Euclidean
    or otherwise never shorter than the coordinate distance.
    """
    return euclidean(positions[state], positions[goal])
