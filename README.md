# Interactive Pathfinding & Heuristic Search System

Python · Tkinter · JSON

State-space search on custom map topologies with an interactive UI: **Breadth-First Search (BFS)** and **A\*** with an admissible Euclidean heuristic.

## Features

- Load city/road graphs from JSON
- Click to pick start and goal on a canvas map
- Side-by-side comparison: path cost, nodes expanded, runtime
- Visual highlight of path, explored set, and frontier
- Sample maps: easy, hard, and no-solution

## Setup

```bash
cd "02-interactive-pathfinding"
# Tkinter is included with standard CPython
python main.py
```

Optional map:

```bash
python main.py --map maps/hard.json
```

## JSON map format

```json
{
  "start": "A",
  "goal": "B",
  "positions": { "A": [0, 0], "B": [1, 1] },
  "edges": [ ["A", "B", 10.0] ]
}
```

## Project layout

```
pathfinding/
  algorithms/   # BFS, A*
  core/         # Node, MapGraph, heuristics
  ui/           # Tkinter application
maps/           # easy.json, hard.json, no_solution.json
main.py
```

## What this demonstrates

Developed state-space exploration algorithms, including A* with admissible heuristics and BFS, on custom map topologies with an interactive JSON-driven interface.
