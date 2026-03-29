# node/token.py — Advanced ephemeral token with HMAC signing and hop tracking

import time
import uuid
import hmac
import hashlib
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import TOKEN_EXPIRY, MAX_HOPS, SECRET_KEY, ENABLE_HMAC


class QuantumToken:
    """
    Advanced one-time-read token with:
    - No-cloning enforcement (read state)
    - Configurable expiry (decoherence)
    - Hop count limit (prevents infinite circulation)
    - HMAC signature (tampering detection)
    - Serialisation for network transport

    Quantum analogies:
      - Superposition → token is "unread" until first observation
      - Collapse      → read_token() collapses state irreversibly
      - Decoherence   → expiry destroys the quantum state over time
      - No-cloning    → token cannot be duplicated across peers
    """

    def __init__(self, message, expiry=None, priority="normal", hops=0, token_id=None):
        self.token_id = token_id or str(uuid.uuid4())[:10]
        self.message = message
        self.priority = priority          # "normal" | "high" | "ephemeral"
        self.expiry = expiry if expiry is not None else TOKEN_EXPIRY
        self.timestamp = time.time()
        self.read = False
        self.hops = hops                  # Number of nodes this token has traversed
        self.signature = self._sign() if ENABLE_HMAC else None

    # ------------------------------------------------------------------
    # HMAC signing — tampering detection
    # ------------------------------------------------------------------
    def _sign(self):
        payload = f"{self.token_id}{self.message}{self.timestamp}"
        return hmac.new(
            SECRET_KEY,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

    def verify(self):
        """Return True if the token's signature is still valid."""
        if not ENABLE_HMAC or self.signature is None:
            return True
        expected = self._sign()
        return hmac.compare_digest(self.signature, expected)

    # ------------------------------------------------------------------
    # State checks
    # ------------------------------------------------------------------
    def is_expired(self):
        return (time.time() - self.timestamp) > self.expiry

    def exceeded_hops(self):
        return self.hops >= MAX_HOPS

    def is_valid(self):
        return not self.read and not self.is_expired() and not self.exceeded_hops()

    # ------------------------------------------------------------------
    # One-time-read (state collapse)
    # ------------------------------------------------------------------
    def read_token(self):
        """
        Consume this token exactly once.
        Returns the message or None if invalid.
        """
        if self.read:
            return None   # Already collapsed
        if self.is_expired():
            return None   # Decoherence
        if self.exceeded_hops():
            return None   # Max hops reached
        if not self.verify():
            return None   # Tampered

        self.read = True
        return self.message

    def increment_hop(self):
        """Called each time a token is forwarded to a new node."""
        self.hops += 1

    # ------------------------------------------------------------------
    # Serialisation (for network transport)
    # ------------------------------------------------------------------
    def to_json(self):
        return json.dumps({
            "token_id": self.token_id,
            "message": self.message,
            "priority": self.priority,
            "expiry": self.expiry,
            "timestamp": self.timestamp,
            "hops": self.hops,
            "signature": self.signature,
        })

    @classmethod
    def from_json(cls, raw):
        """Reconstruct a QuantumToken from a JSON string received over the network."""
        try:
            data = json.loads(raw)
            token = cls.__new__(cls)
            token.token_id = data["token_id"]
            token.message = data["message"]
            token.priority = data.get("priority", "normal")
            token.expiry = data["expiry"]
            token.timestamp = data["timestamp"]
            token.hops = data.get("hops", 0)
            token.signature = data.get("signature")
            token.read = False   # Always starts unread on the receiving side
            return token
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid token JSON: {e}")

    # ------------------------------------------------------------------
    def status(self):
        if self.read:
            return "consumed"
        if self.is_expired():
            return "expired"
        if self.exceeded_hops():
            return f"hop-limit ({self.hops}/{MAX_HOPS})"
        remaining = self.expiry - (time.time() - self.timestamp)
        return f"active ({remaining:.1f}s left, hop {self.hops}/{MAX_HOPS})"

    def __repr__(self):
        return (
            f"QuantumToken(id={self.token_id}, priority={self.priority}, "
            f"status={self.status()})"
        )
