# node/encounter_simulator.py — Simulates link failures and recoveries

import random
import threading
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PEER_PORTS, FAILURE_SIMULATION_INTERVAL, PENALTY


class LinkFailureSimulator:
    """
    Simulates random link failures and recoveries to test self-healing behaviour.

    Inspired by ant colony behaviour:
    - Ants that find a broken path stop reinforcing it
    - Other ants explore alternative routes
    - The network converges to a new optimal path
    """

    def __init__(self, pheromone_table, logger, node_id):
        self.pheromone_table = pheromone_table
        self.logger = logger
        self.node_id = node_id
        self.blocked_peers = set()   # Currently "failed" links
        self.running = False

    def is_blocked(self, peer):
        """Returns True if this link is currently simulated as failed."""
        return peer in self.blocked_peers

    def _simulate_failure(self):
        """Randomly fail or recover a link."""
        if not PEER_PORTS:
            return

        peer = random.choice(PEER_PORTS)

        if peer in self.blocked_peers:
            # Recover the link
            self.blocked_peers.discard(peer)
            self.logger.log(f"LINK RECOVERY: Node {self.node_id} ↔ {peer} restored 🔗")
        else:
            # Fail the link — penalize pheromone to simulate path detection
            self.blocked_peers.add(peer)
            self.pheromone_table.penalize(peer, PENALTY * 3)
            self.logger.log(
                f"LINK FAILURE: Node {self.node_id} ↔ {peer} broken ✂ "
                f"(pheromone penalized)"
            )

    def run(self):
        """Start the failure simulation loop."""
        self.running = True

        def _loop():
            # Wait before first failure so network can warm up
            time.sleep(FAILURE_SIMULATION_INTERVAL)
            while self.running:
                self._simulate_failure()
                time.sleep(FAILURE_SIMULATION_INTERVAL)

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread

    def stop(self):
        self.running = False
