# delivery_table.py

class DeliveryTable:
    def __init__(self):
        self.table = {}  # {peer_port: probability}

    def update_probability(self, peer, prob):
        """Update the delivery probability for a given peer."""
        self.table[peer] = prob
        print(f"[TABLE] Updated probability for peer {peer}: {prob}")

    def get_probability(self, peer):
        """Return the delivery probability for a peer, default 0.0 if unknown."""
        return self.table.get(peer, 0.0)

    def get_best_candidates(self, threshold):
        """Return list of peers with delivery probability >= threshold."""
        return [peer for peer, prob in self.table.items() if prob >= threshold]

    def display(self):
        """Print current delivery table."""
        print("\n[TABLE] Current Delivery Probability Table:")
        if not self.table:
            print("  (empty)")
        for peer, prob in self.table.items():
            bar = "#" * int(prob * 20)
            print(f"  Port {peer}: {prob:.2f}  [{bar:<20}]")
        print()
