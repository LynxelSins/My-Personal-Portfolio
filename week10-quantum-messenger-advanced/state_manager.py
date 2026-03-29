# node/state_manager.py — Network state manager: seen-token cache + probabilistic delivery

import random
import time
import collections
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DELIVERY_PROBABILITY, SEEN_CACHE_SIZE


class StateManager:
    """
    Manages two aspects of quantum-inspired network state:

    1. SEEN TOKEN CACHE
       Tracks token IDs this node has already processed.
       Prevents a token from being re-delivered if it loops back
       (analogous to the no-cloning / no-reuse rule in QKD).

    2. PROBABILISTIC DELIVERY
       Each send attempt has a configurable success probability.
       Models real-world channel uncertainty and — conceptually —
       the probabilistic nature of quantum measurements.

       delivery_probability = 1.0 → deterministic (classical network)
       delivery_probability < 1.0 → probabilistic (quantum-inspired)
    """

    def __init__(self, node_id):
        self.node_id = node_id
        # OrderedDict used as a bounded LRU cache
        self._seen = collections.OrderedDict()
        self._stats = {
            "attempted": 0,
            "collapsed": 0,   # Probabilistic failures
            "duplicates_blocked": 0,
            "tampered_blocked": 0,
        }

    # ------------------------------------------------------------------
    # Seen-token cache
    # ------------------------------------------------------------------
    def mark_seen(self, token_id):
        """Record that this token has been processed."""
        if token_id in self._seen:
            self._seen.move_to_end(token_id)
        else:
            if len(self._seen) >= SEEN_CACHE_SIZE:
                self._seen.popitem(last=False)   # Evict oldest
            self._seen[token_id] = time.time()

    def already_seen(self, token_id):
        """Return True if this token was already processed by this node."""
        return token_id in self._seen

    # ------------------------------------------------------------------
    # Probabilistic delivery (quantum collapse model)
    # ------------------------------------------------------------------
    def attempt_delivery(self):
        """
        Simulate a probabilistic channel.
        Returns True if the delivery attempt "succeeds" this time.

        Conceptual mapping:
          - The token is in superposition until the send attempt
          - The channel "measures" the attempt and collapses it to
            success or failure with the configured probability
        """
        self._stats["attempted"] += 1
        success = random.random() < DELIVERY_PROBABILITY
        if not success:
            self._stats["collapsed"] += 1
        return success

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def validate_token(self, token, logger):
        """
        Full validation pipeline for an incoming token.
        Returns True if the token should be processed.
        """
        # Duplicate check
        if self.already_seen(token.token_id):
            self._stats["duplicates_blocked"] += 1
            logger.log(
                f"DUPLICATE BLOCKED: token {token.token_id} already seen by node {self.node_id}"
            )
            return False

        # Tampering check
        if not token.verify():
            self._stats["tampered_blocked"] += 1
            logger.log(
                f"TAMPER DETECTED: token {token.token_id} signature invalid — discarded"
            )
            return False

        # Validity (expiry / hops)
        if not token.is_valid():
            logger.log(
                f"INVALID TOKEN: {token.token_id} — {token.status()}"
            )
            return False

        return True

    # ------------------------------------------------------------------
    def print_stats(self):
        a = self._stats["attempted"]
        c = self._stats["collapsed"]
        collapse_rate = (c / a * 100) if a > 0 else 0.0
        print(
            f"\n[STATE {self.node_id}] Probabilistic delivery stats:\n"
            f"  Attempts         : {a}\n"
            f"  Collapses (fail) : {c}  ({collapse_rate:.1f}%)\n"
            f"  Duplicates blocked: {self._stats['duplicates_blocked']}\n"
            f"  Tampered blocked : {self._stats['tampered_blocked']}\n"
            f"  Seen cache size  : {len(self._seen)}/{SEEN_CACHE_SIZE}\n"
        )
