# token.py
import time
import uuid

from config import TOKEN_EXPIRY


class Token:
    """
    Represents a quantum-inspired one-time-read token.

    Key properties (inspired by quantum mechanics):
    - No-cloning: once read, the token cannot be read again
    - Collapse:   reading the token "collapses" its state — it becomes consumed
    - Expiry:     stale tokens expire, preventing indefinite circulation
    """

    def __init__(self, message, expiry=None):
        self.token_id = str(uuid.uuid4())[:8]   # Short unique ID
        self.message = message
        self.read = False                         # Has this token been consumed?
        self.timestamp = time.time()
        self.expiry = expiry if expiry is not None else TOKEN_EXPIRY

    # ------------------------------------------------------------------
    # Core one-time-read behaviour
    # ------------------------------------------------------------------
    def is_expired(self):
        """Return True if the token has passed its expiry window."""
        return (time.time() - self.timestamp) > self.expiry

    def read_token(self):
        """
        Attempt to read (consume) this token.
        Returns the message on the first read; None on any subsequent attempt
        or if the token has expired.

        Analogy: measuring a quantum state collapses the superposition.
        Once observed, the state is fixed and cannot be re-measured.
        """
        if self.read:
            print(f"[TOKEN {self.token_id}] ✗ Already consumed (collapsed state)")
            return None
        if self.is_expired():
            print(f"[TOKEN {self.token_id}] ✗ Expired — token is no longer valid")
            return None
        self.read = True
        age = round(time.time() - self.timestamp, 2)
        print(f"[TOKEN {self.token_id}] ✓ Consumed after {age}s — state collapsed")
        return self.message

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def status(self):
        if self.read:
            return "consumed"
        if self.is_expired():
            return "expired"
        remaining = self.expiry - (time.time() - self.timestamp)
        return f"active ({remaining:.1f}s remaining)"

    def __repr__(self):
        return f"Token(id={self.token_id}, status={self.status()}, msg='{self.message[:30]}')"
