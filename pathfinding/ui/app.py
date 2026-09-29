"""Tkinter interactive pathfinding application."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Set, Tuple

from pathfinding.algorithms import a_star_search, bfs_search
from pathfinding.core.graph import MapGraph


COLORS = {
    "bg": "#1a1d23",
    "panel": "#242933",
    "canvas": "#0f1218",
    "edge": "#4a5568",
    "node": "#718096",
    "start": "#38a169",
    "goal": "#e53e3e",
    "path": "#f6ad55",
    "explored": "#4299e1",
    "frontier": "#9f7aea",
    "text": "#e2e8f0",
    "accent": "#63b3ed",
}


class PathfindingApp:
    def __init__(self, root: tk.Tk, initial_map: Optional[Path] = None) -> None:
        self.root = root
        self.root.title("Interactive Pathfinding & Heuristic Search")
        self.root.geometry("1100x720")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(900, 600)

        self.graph: Optional[MapGraph] = None
        self.start: Optional[str] = None
        self.goal: Optional[str] = None
        self.node_screen: Dict[str, Tuple[float, float]] = {}
        self.selection_mode = "start"  # start | goal
        self.last_bfs = None
        self.last_astar = None
        self.show_explored = tk.BooleanVar(value=True)

        self._build_ui()
        if initial_map and initial_map.exists():
            self.load_map(initial_map)

    def _build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=COLORS["panel"])
        style.configure("TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("TButton", padding=6)
        style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["text"])

        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = ttk.Frame(main, width=280)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        ttk.Label(left, text="Controls", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Button(left, text="Load JSON Map…", command=self.browse_map).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="Reset Selection", command=self.reset_selection).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="Run BFS + A*", command=self.run_search).pack(fill=tk.X, pady=3)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12)
        ttk.Label(left, text="Click a city: set Start, then Goal.", wraplength=250).pack(anchor="w")
        self.lbl_mode = ttk.Label(left, text="Mode: select START", foreground=COLORS["accent"])
        self.lbl_mode.pack(anchor="w", pady=6)
        self.lbl_start = ttk.Label(left, text="Start: —")
        self.lbl_start.pack(anchor="w")
        self.lbl_goal = ttk.Label(left, text="Goal: —")
        self.lbl_goal.pack(anchor="w")

        ttk.Checkbutton(
            left, text="Highlight explored / frontier", variable=self.show_explored, command=self.redraw
        ).pack(anchor="w", pady=10)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(left, text="Comparison", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.stats = tk.Text(
            left,
            height=16,
            width=34,
            bg=COLORS["canvas"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            font=("Consolas", 9),
            wrap=tk.WORD,
        )
        self.stats.pack(fill=tk.BOTH, expand=True, pady=6)
        self.stats.insert("1.0", "Load a map and select start/goal to compare BFS vs A*.")
        self.stats.configure(state=tk.DISABLED)

        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(right, bg=COLORS["canvas"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

        legend = ttk.Frame(right)
        legend.pack(fill=tk.X, pady=(6, 0))
        for label, color in [
            ("Start", COLORS["start"]),
            ("Goal", COLORS["goal"]),
            ("Path", COLORS["path"]),
            ("Explored", COLORS["explored"]),
            ("Frontier", COLORS["frontier"]),
        ]:
            swatch = tk.Canvas(legend, width=14, height=14, bg=color, highlightthickness=0)
            swatch.pack(side=tk.LEFT, padx=(0, 4))
            ttk.Label(legend, text=label).pack(side=tk.LEFT, padx=(0, 12))

    def browse_map(self) -> None:
        path = filedialog.askopenfilename(
            title="Select map JSON",
            filetypes=[("JSON maps", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).resolve().parents[2] / "maps"),
        )
        if path:
            self.load_map(Path(path))

    def load_map(self, path: Path) -> None:
        try:
            self.graph = MapGraph.from_json(path)
        except Exception as exc:
            messagebox.showerror("Load error", str(exc))
            return
        self.start = self.graph.default_start
        self.goal = self.graph.default_goal
        self.selection_mode = "goal" if self.start else "start"
        self.last_bfs = self.last_astar = None
        self._update_labels()
        self.redraw()
        self._set_stats(f"Loaded: {path.name}\nNodes: {len(self.graph.nodes)}\nSelect start & goal, then Run.")

    def reset_selection(self) -> None:
        self.start = self.goal = None
        self.selection_mode = "start"
        self.last_bfs = self.last_astar = None
        self._update_labels()
        self.redraw()

    def _update_labels(self) -> None:
        self.lbl_start.config(text=f"Start: {self.start or '—'}")
        self.lbl_goal.config(text=f"Goal: {self.goal or '—'}")
        mode = "select START" if self.selection_mode == "start" else "select GOAL"
        self.lbl_mode.config(text=f"Mode: {mode}")

    def _set_stats(self, text: str) -> None:
        self.stats.configure(state=tk.NORMAL)
        self.stats.delete("1.0", tk.END)
        self.stats.insert("1.0", text)
        self.stats.configure(state=tk.DISABLED)

    def on_canvas_click(self, event: tk.Event) -> None:
        if not self.graph:
            return
        hit = self._hit_node(event.x, event.y)
        if not hit:
            return
        if self.selection_mode == "start":
            self.start = hit
            self.goal = None
            self.selection_mode = "goal"
            self.last_bfs = self.last_astar = None
        else:
            if hit == self.start:
                return
            self.goal = hit
            self.selection_mode = "start"
        self._update_labels()
        self.redraw()

    def _hit_node(self, x: float, y: float, radius: float = 16) -> Optional[str]:
        for name, (sx, sy) in self.node_screen.items():
            if (x - sx) ** 2 + (y - sy) ** 2 <= radius ** 2:
                return name
        return None

    def run_search(self) -> None:
        if not self.graph or not self.start or not self.goal:
            messagebox.showinfo("Missing input", "Load a map and select both start and goal.")
            return
        self.last_bfs = bfs_search(self.graph, self.start, self.goal)
        self.last_astar = a_star_search(self.graph, self.start, self.goal)
        self._set_stats(self._format_comparison())
        self.redraw()

    def _format_comparison(self) -> str:
        lines = [f"Route: {self.start} → {self.goal}", ""]
        for title, res in [("BFS (uninformed)", self.last_bfs), ("A* (informed)", self.last_astar)]:
            lines.append(f"=== {title} ===")
            if res and res.found:
                lines.append(f"Path : {' → '.join(res.path)}")
                lines.append(f"Cost : {res.cost:.2f}")
                lines.append(f"Expanded: {res.nodes_expanded}")
                lines.append(f"Time : {res.elapsed_sec * 1000:.3f} ms")
            else:
                lines.append("No path found.")
            lines.append("")
        if self.last_bfs and self.last_astar and self.last_bfs.found and self.last_astar.found:
            saved = self.last_bfs.nodes_expanded - self.last_astar.nodes_expanded
            lines.append(f"A* expanded {saved} fewer nodes than BFS." if saved > 0 else "Node expansion similar.")
        return "\n".join(lines)

    def redraw(self) -> None:
        self.canvas.delete("all")
        if not self.graph:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2 or 400,
                self.canvas.winfo_height() // 2 or 300,
                text="Load a JSON map to begin",
                fill=COLORS["text"],
                font=("Segoe UI", 14),
            )
            return

        w = max(self.canvas.winfo_width(), 100)
        h = max(self.canvas.winfo_height(), 100)
        xs = [p[0] for p in self.graph.positions.values()]
        ys = [p[1] for p in self.graph.positions.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        pad = 50
        span_x = max(max_x - min_x, 1e-6)
        span_y = max(max_y - min_y, 1e-6)

        def to_screen(name: str) -> Tuple[float, float]:
            x, y = self.graph.positions[name]
            sx = pad + (x - min_x) / span_x * (w - 2 * pad)
            sy = h - (pad + (y - min_y) / span_y * (h - 2 * pad))
            return sx, sy

        self.node_screen = {n: to_screen(n) for n in self.graph.nodes}

        drawn = set()
        for u, neighs in self.graph.edges.items():
            for v in neighs:
                key = tuple(sorted((u, v)))
                if key in drawn:
                    continue
                drawn.add(key)
                x1, y1 = self.node_screen[u]
                x2, y2 = self.node_screen[v]
                self.canvas.create_line(x1, y1, x2, y2, fill=COLORS["edge"], width=2)

        path_set: Set[str] = set()
        path_edges: Set[Tuple[str, str]] = set()
        explored: Set[str] = set()
        frontier: Set[str] = set()
        result = self.last_astar or self.last_bfs
        if result and result.found:
            path_set = set(result.path)
            for i in range(len(result.path) - 1):
                path_edges.add(tuple(sorted((result.path[i], result.path[i + 1]))))
            if self.show_explored.get():
                explored = set(result.explored) - path_set
                frontier = set(result.frontier_final) - path_set - explored

        for u, v in path_edges:
            x1, y1 = self.node_screen[u]
            x2, y2 = self.node_screen[v]
            self.canvas.create_line(x1, y1, x2, y2, fill=COLORS["path"], width=4)

        r = 12
        for name, (sx, sy) in self.node_screen.items():
            if name == self.start:
                color = COLORS["start"]
            elif name == self.goal:
                color = COLORS["goal"]
            elif name in path_set:
                color = COLORS["path"]
            elif name in frontier:
                color = COLORS["frontier"]
            elif name in explored:
                color = COLORS["explored"]
            else:
                color = COLORS["node"]
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=color, outline="#fff", width=1)
            self.canvas.create_text(sx, sy - 20, text=name, fill=COLORS["text"], font=("Segoe UI", 8, "bold"))


def launch(map_path: Optional[str] = None) -> None:
    root = tk.Tk()
    maps_dir = Path(__file__).resolve().parents[2] / "maps"
    initial = Path(map_path) if map_path else maps_dir / "easy.json"
    PathfindingApp(root, initial_map=initial)
    root.mainloop()
