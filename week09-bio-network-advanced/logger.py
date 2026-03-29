# utils/logger.py — Event logging and statistics for bio-routing network

import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import LOG_FILE


class Logger:
    """
    Logs routing events and tracks statistics for the self-healing network.
    Supports pheromone history export for visualization (Extension C).
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.log_path = f"node{node_id}_{LOG_FILE}"
        self.stats = {
            "sent": 0,
            "failed": 0,
            "queued": 0,
            "healed": 0,     # Times routing recovered after a failure
            "decay_cycles": 0,
        }
        with open(self.log_path, "w") as f:
            f.write(
                f"=== Bio-Routing Node {node_id} — started {self._ts()} ===\n"
            )

    def _ts(self):
        return time.strftime("%H:%M:%S")

    def log(self, message):
        entry = f"[{self._ts()}] {message}"
        print(entry)
        with open(self.log_path, "a") as f:
            f.write(entry + "\n")

    # ------------------------------------------------------------------
    # Stat recording
    # ------------------------------------------------------------------
    def record_sent(self):       self.stats["sent"] += 1
    def record_failed(self):     self.stats["failed"] += 1
    def record_queued(self):     self.stats["queued"] += 1
    def record_healed(self):     self.stats["healed"] += 1
    def record_decay(self):      self.stats["decay_cycles"] += 1

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def print_stats(self):
        total = self.stats["sent"] + self.stats["failed"]
        rate = (self.stats["sent"] / total * 100) if total > 0 else 0.0
        report = (
            f"\n{'='*44}\n"
            f"  Bio-Routing Node {self.node_id} — Statistics\n"
            f"{'='*44}\n"
            f"  Sent (success)  : {self.stats['sent']}  ({rate:.1f}%)\n"
            f"  Failed          : {self.stats['failed']}\n"
            f"  Queued          : {self.stats['queued']}\n"
            f"  Self-heals      : {self.stats['healed']}\n"
            f"  Decay cycles    : {self.stats['decay_cycles']}\n"
            f"{'='*44}\n"
        )
        print(report)
        with open(self.log_path, "a") as f:
            f.write(report)

    def export_pheromone_history(self, history):
        """
        Write pheromone history to a CSV for visualization (Extension C).
        Format: elapsed_seconds, peer_port, pheromone_value
        """
        csv_path = f"node{self.node_id}_pheromone_history.csv"
        with open(csv_path, "w") as f:
            f.write("elapsed_seconds,peer_port,pheromone\n")
            for elapsed, snapshot in history:
                for peer, pher in snapshot.items():
                    f.write(f"{elapsed},{peer},{pher:.4f}\n")
        self.log(f"Pheromone history exported → {csv_path}")
        return csv_path
