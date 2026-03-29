# node/delivery_table.py — Adaptive delivery probability table

import time

class DeliveryTable:
    """
    Maintains delivery probabilities for each peer.
    Supports adaptive updates based on encounter history.
    """

    # Aging factor: reduce probability over time if no encounters
    AGING_FACTOR = 0.98
    # Learning rate: how much each new encounter shifts the probability
    LEARNING_RATE = 0.2

    def __init__(self):
        # {peer_port: {"prob": float, "encounters": int, "last_seen": float}}
        self.table = {}

    def _init_peer(self, peer):
        if peer not in self.table:
            self.table[peer] = {
                "prob": 0.0,
                "encounters": 0,
                "last_seen": None
            }

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------
    def update_probability(self, peer, prob):
        """Directly set the delivery probability for a peer."""
        self._init_peer(peer)
        self.table[peer]["prob"] = max(0.0, min(1.0, prob))

    def get_probability(self, peer):
        """Return delivery probability for a peer (0.0 if unknown)."""
        return self.table.get(peer, {}).get("prob", 0.0)

    def get_best_candidates(self, threshold):
        """Return peers whose delivery probability meets the threshold."""
        return [
            peer for peer, info in self.table.items()
            if info["prob"] >= threshold
        ]

    # ------------------------------------------------------------------
    # Extension A: Dynamic / adaptive probability updates
    # ------------------------------------------------------------------
    def record_encounter(self, peer):
        """
        Called when this node meets 'peer'.
        Increases probability using exponential moving average.
        """
        self._init_peer(peer)
        entry = self.table[peer]
        entry["encounters"] += 1
        entry["last_seen"] = time.time()

        old_prob = entry["prob"]
        # EMA update: move probability toward 1.0 on each encounter
        entry["prob"] = old_prob + self.LEARNING_RATE * (1.0 - old_prob)
        entry["prob"] = min(1.0, entry["prob"])

        return entry["prob"]

    def record_delivery_success(self, peer):
        """Slightly boost probability when a message is successfully delivered."""
        self._init_peer(peer)
        entry = self.table[peer]
        entry["prob"] = min(1.0, entry["prob"] + 0.05)

    def record_delivery_failure(self, peer):
        """Slightly reduce probability when delivery fails."""
        self._init_peer(peer)
        entry = self.table[peer]
        entry["prob"] = max(0.0, entry["prob"] - 0.1)

    def age_probabilities(self):
        """
        Gradually decay all probabilities over time.
        Call periodically to model nodes drifting apart.
        """
        for peer in self.table:
            self.table[peer]["prob"] *= self.AGING_FACTOR

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def display(self):
        """Print a formatted view of the delivery table."""
        print("\n╔══ Delivery Probability Table ══╗")
        if not self.table:
            print("║  (empty)                       ║")
        for peer, info in self.table.items():
            prob = info["prob"]
            enc  = info["encounters"]
            bar  = "█" * int(prob * 15)
            last = "never"
            if info["last_seen"]:
                ago = time.time() - info["last_seen"]
                last = f"{ago:.0f}s ago"
            print(f"║  Port {peer}: {prob:.2f}  [{bar:<15}]  enc={enc}  last={last}")
        print("╚════════════════════════════════╝\n")
