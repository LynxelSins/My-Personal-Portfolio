# pheromone_table.py

from config import DECAY_FACTOR


class PheromoneTable:
    """
    Maintains pheromone levels for each peer, inspired by Ant Colony Optimization (ACO).

    - Pheromone increases when a message is successfully delivered (reinforcement)
    - Pheromone decreases over time (decay / evaporation)
    - Peers with higher pheromone are preferred for forwarding
    """

    def __init__(self):
        self.table = {}  # {peer_port: pheromone_value}

    def reinforce(self, peer, value):
        """Increase pheromone on a path after a successful delivery."""
        self.table[peer] = self.table.get(peer, 0.0) + value
        print(f"[PHEROMONE] ↑ Reinforced port {peer}: {self.table[peer]:.3f}")

    def decay(self):
        """
        Evaporate pheromone on all paths.
        Mimics how ant trails fade when not re-reinforced.
        """
        for peer in self.table:
            self.table[peer] *= DECAY_FACTOR
        print(f"[PHEROMONE] 💨 Decayed all paths (factor={DECAY_FACTOR})")

    def penalize(self, peer, penalty=0.05):
        """Reduce pheromone slightly on a path that failed delivery."""
        if peer in self.table:
            self.table[peer] = max(0.0, self.table[peer] - penalty)
            print(f"[PHEROMONE] ↓ Penalized port {peer}: {self.table[peer]:.3f}")

    def get_best_candidates(self, threshold):
        """Return peers whose pheromone level meets or exceeds the threshold."""
        return sorted(
            [peer for peer, pher in self.table.items() if pher >= threshold],
            key=lambda p: self.table[p],
            reverse=True  # Highest pheromone first
        )

    def display(self):
        """Print the current pheromone table."""
        print("\n[PHEROMONE TABLE]")
        if not self.table:
            print("  (empty)")
            return
        for peer, pher in sorted(self.table.items()):
            bar = "█" * int(min(pher, 5.0) / 5.0 * 20)
            print(f"  Port {peer}: {pher:.3f}  [{bar:<20}]")
        print()
