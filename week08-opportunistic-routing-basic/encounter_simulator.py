# node/encounter_simulator.py — Simulates random mobile node encounters

import random
import threading
import time
import sys
import os

# Allow imports from parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PEER_PORTS, ENCOUNTER_INTERVAL, ENCOUNTER_PROB_MIN, ENCOUNTER_PROB_MAX


class EncounterSimulator:
    """
    Simulates a mobile wildlife sensor node moving through an environment.
    Randomly 'encounters' peers and updates delivery probabilities accordingly.

    Real-world analogy:
      - Two animals with GPS collars come within radio range of each other
      - They exchange data opportunistically during the brief encounter window
    """

    def __init__(self, delivery_table, logger, node_id):
        self.delivery_table = delivery_table
        self.logger = logger
        self.node_id = node_id
        self.running = False

    def _simulate_encounter(self):
        """
        Pick a random peer, decide if an encounter happens,
        and update delivery probabilities accordingly.
        """
        peer = random.choice(PEER_PORTS)
        # Probability that paths cross at this moment
        encounter_happened = random.random() < random.uniform(
            ENCOUNTER_PROB_MIN, ENCOUNTER_PROB_MAX
        )

        if encounter_happened:
            new_prob = self.delivery_table.record_encounter(peer)
            self.logger.log(
                f"ENCOUNTER: Node {self.node_id} met peer {peer} → prob now {new_prob:.2f}"
            )
            return peer
        else:
            # Paths didn't cross — age probabilities slightly
            self.delivery_table.age_probabilities()
            self.logger.log(
                f"NO ENCOUNTER: Node {self.node_id} drifted from peers (probabilities aged)"
            )
            return None

    def run(self):
        """Start the encounter simulation loop in a background thread."""
        self.running = True

        def _loop():
            while self.running:
                encountered_peer = self._simulate_encounter()
                if encountered_peer:
                    print(
                        f"[SIM {self.node_id}] 🐾 Encountered peer {encountered_peer}"
                    )
                else:
                    print(f"[SIM {self.node_id}] 🌿 No encounter this cycle")
                time.sleep(ENCOUNTER_INTERVAL)

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread

    def stop(self):
        self.running = False
