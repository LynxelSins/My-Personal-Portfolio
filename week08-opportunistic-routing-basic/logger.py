# utils/logger.py — Logging and statistics for the wildlife network

import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import LOG_FILE


class Logger:
    """
    Logs network events to both console and file.
    Tracks delivery statistics for analysis.
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.log_path = f"node{node_id}_{LOG_FILE}"
        self.stats = {
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "queued": 0,
            "expired": 0,
        }
        # Create/clear the log file
        with open(self.log_path, "w") as f:
            f.write(f"=== Wildlife Node {node_id} Log — started {self._timestamp()} ===\n")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _timestamp(self):
        return time.strftime("%H:%M:%S")

    def log(self, message):
        """Write a timestamped message to console and log file."""
        entry = f"[{self._timestamp()}] {message}"
        print(entry)
        with open(self.log_path, "a") as f:
            f.write(entry + "\n")

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    def record_attempt(self):
        self.stats["attempts"] += 1

    def record_success(self):
        self.stats["successes"] += 1

    def record_failure(self):
        self.stats["failures"] += 1

    def record_queued(self):
        self.stats["queued"] += 1

    def record_expired(self):
        self.stats["expired"] += 1

    def print_stats(self):
        """Print a summary of delivery statistics."""
        total = self.stats["attempts"]
        success = self.stats["successes"]
        rate = (success / total * 100) if total > 0 else 0.0

        summary = (
            f"\n{'='*40}\n"
            f"  Node {self.node_id} — Delivery Statistics\n"
            f"{'='*40}\n"
            f"  Attempts  : {total}\n"
            f"  Successes : {success}  ({rate:.1f}%)\n"
            f"  Failures  : {self.stats['failures']}\n"
            f"  Queued    : {self.stats['queued']}\n"
            f"  Expired   : {self.stats['expired']}\n"
            f"{'='*40}\n"
        )
        print(summary)
        with open(self.log_path, "a") as f:
            f.write(summary)
