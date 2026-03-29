# utils/logger.py — Logging and analytics for quantum-secure messenger

import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import LOG_FILE


class Logger:
    """
    Records token lifecycle events and delivery statistics.
    Supports token state transition export for Extension C visualisation.
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.log_path = f"node{node_id}_{LOG_FILE}"
        self.stats = {
            "created": 0,
            "sent": 0,
            "received": 0,
            "consumed": 0,
            "expired": 0,
            "tampered": 0,
            "duplicates": 0,
            "collapsed": 0,    # Probabilistic channel failures
        }
        # Token state transition history: [(timestamp, token_id, event)]
        self.transitions = []

        with open(self.log_path, "w") as f:
            f.write(
                f"=== Quantum Messenger Node {node_id} — {self._ts()} ===\n"
            )

    def _ts(self):
        return time.strftime("%H:%M:%S")

    def log(self, message):
        entry = f"[{self._ts()}] {message}"
        print(entry)
        with open(self.log_path, "a") as f:
            f.write(entry + "\n")

    # ------------------------------------------------------------------
    # Stat helpers
    # ------------------------------------------------------------------
    def record(self, event, token_id=None):
        """Record a stat event and optionally a state transition."""
        if event in self.stats:
            self.stats[event] += 1
        if token_id:
            self.transitions.append((time.time(), token_id, event))

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def print_stats(self):
        total_sent = self.stats["sent"] + self.stats["collapsed"]
        delivery_rate = (
            self.stats["sent"] / total_sent * 100 if total_sent > 0 else 0.0
        )
        report = (
            f"\n{'='*46}\n"
            f"  Quantum Messenger Node {self.node_id} — Statistics\n"
            f"{'='*46}\n"
            f"  Tokens created   : {self.stats['created']}\n"
            f"  Tokens sent      : {self.stats['sent']}  ({delivery_rate:.1f}% channel success)\n"
            f"  Tokens received  : {self.stats['received']}\n"
            f"  Tokens consumed  : {self.stats['consumed']}\n"
            f"  Expired          : {self.stats['expired']}\n"
            f"  Collapsed (prob) : {self.stats['collapsed']}\n"
            f"  Tampered blocked : {self.stats['tampered']}\n"
            f"  Duplicates blocked: {self.stats['duplicates']}\n"
            f"{'='*46}\n"
        )
        print(report)
        with open(self.log_path, "a") as f:
            f.write(report)

    def export_transitions(self):
        """Export token state transitions to CSV for visualisation (Extension C)."""
        if not self.transitions:
            return None
        csv_path = f"node{self.node_id}_transitions.csv"
        t0 = self.transitions[0][0]
        with open(csv_path, "w") as f:
            f.write("elapsed_seconds,token_id,event\n")
            for ts, tid, event in self.transitions:
                f.write(f"{round(ts - t0, 2)},{tid},{event}\n")
        self.log(f"Transition history exported → {csv_path}")
        return csv_path
