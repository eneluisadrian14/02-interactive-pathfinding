"""Launch Interactive Pathfinding & Heuristic Search."""

from __future__ import annotations

import argparse
from pathlib import Path

from pathfinding.ui.app import launch


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive Pathfinding (BFS + A*)")
    parser.add_argument(
        "--map",
        type=str,
        default=None,
        help="Path to a JSON map (default: maps/easy.json)",
    )
    args = parser.parse_args()
    launch(args.map)


if __name__ == "__main__":
    main()
