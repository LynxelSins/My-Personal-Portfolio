# node/pheromone_table.py — Advanced pheromone table with multi-hop support

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DECAY_FACTOR, PENALTY


class PheromoneTable:
    """
    Advanced pheromone table supporting:
    - Direct peer pheromone tracking
    - Multi-hop path pheromone (Extension B concept)
    - Round-trip reinforcement
    - History for visualization
    """

    def __init__(self, node_id):
        self.node_id = node_id
        # Direct peers: {peer_port: {"pheromone": float, "successes": int, "failures": int}}
        self.table = {}
        # Multi-hop paths: {destination: {via_peer: pheromone}}
        self.multihop = {}
        # History for plotting: [(timestamp, {peer: pheromone})]
        self.history = []

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------
    def _init_peer(self, peer):
        if peer not in self.table:
            self.table[peer] = {"pheromone": 0.0, "successes": 0, "failures": 0}

    def reinforce(self, peer, value):
        """Deposit pheromone on a successful path."""
        self._init_peer(peer)
        self.table[peer]["pheromone"] += value
        self.table[peer]["successes"] += 1

    def penalize(self, peer, value=None):
        """Reduce pheromone on a failed path."""
        self._init_peer(peer)
        amount = value if value is not None else PENALTY
        self.table[peer]["pheromone"] = max(0.0, self.table[peer]["pheromone"] - amount)
        self.table[peer]["failures"] += 1

    def decay(self):
        """Evaporate pheromone on all direct paths."""
        for peer in self.table:
            self.table[peer]["pheromone"] *= DECAY_FACTOR
        # Also decay multihop paths
        for dest in self.multihop:
            for via in self.multihop[dest]:
                self.multihop[dest][via] *= DECAY_FACTOR
        # Record history snapshot
        self.history.append((
            time.time(),
            {peer: info["pheromone"] for peer, info in self.table.items()}
        ))

    def get_pheromone(self, peer):
        return self.table.get(peer, {}).get("pheromone", 0.0)

    def get_best_candidates(self, threshold):
        """Return peers above threshold, sorted best-first."""
        return sorted(
            [peer for peer, info in self.table.items()
             if info["pheromone"] >= threshold],
            key=lambda p: self.table[p]["pheromone"],
            reverse=True
        )

    # ------------------------------------------------------------------
    # Extension B: Multi-hop pheromone
    # ------------------------------------------------------------------
    def update_multihop(self, destination, via_peer, value):
        """Record pheromone for a path to a non-direct destination via a peer."""
        if destination not in self.multihop:
            self.multihop[destination] = {}
        self.multihop[destination][via_peer] = (
            self.multihop[destination].get(via_peer, 0.0) + value
        )

    def get_best_multihop(self, destination, threshold=0.1):
        """Return the best next-hop peer for reaching a distant destination."""
        paths = self.multihop.get(destination, {})
        viable = [(via, pher) for via, pher in paths.items() if pher >= threshold]
        if not viable:
            return None
        return max(viable, key=lambda x: x[1])[0]

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def display(self):
        print(f"\n╔══ Pheromone Table — Node {self.node_id} ══╗")
        if not self.table:
            print("║  (empty)")
        for peer, info in sorted(self.table.items()):
            pher = info["pheromone"]
            bar = "█" * int(min(pher / 2.0, 1.0) * 18)
            s, f = info["successes"], info["failures"]
            print(f"║  Port {peer}: {pher:.3f}  [{bar:<18}]  ✓{s} ✗{f}")
        if self.multihop:
            print("║  — Multi-hop paths —")
            for dest, paths in self.multihop.items():
                best_via = max(paths, key=paths.get) if paths else "none"
                print(f"║  → {dest} via {best_via}: {paths.get(best_via, 0):.3f}")
        print("╚" + "═" * 36 + "╝\n")

    def get_history_summary(self):
        """Return a list of (elapsed_seconds, pheromone_snapshot) tuples."""
        if not self.history:
            return []
        t0 = self.history[0][0]
        return [(round(t - t0, 1), snap) for t, snap in self.history]
