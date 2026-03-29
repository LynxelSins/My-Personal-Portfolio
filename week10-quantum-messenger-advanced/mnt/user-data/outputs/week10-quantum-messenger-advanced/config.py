# config.py — Quantum-Secure Messenger (Advanced Lab)
HOST = "127.0.0.1"
BASE_PORT = 11100
PEER_PORTS = [11101, 11102]
BUFFER_SIZE = 2048

# Token settings
TOKEN_EXPIRY = 15            # seconds before a token expires
SHORT_EXPIRY = 5             # used for high-priority ephemeral tokens
UPDATE_INTERVAL = 4          # forwarding cycle interval (seconds)

# Probabilistic delivery (quantum collapse simulation)
# Each send attempt succeeds with this probability, modelling network uncertainty
DELIVERY_PROBABILITY = 0.85

# Multi-hop settings
MAX_HOPS = 3                 # token discarded after this many hops
SEEN_CACHE_SIZE = 200        # max token IDs to remember (prevent re-delivery)

# Security
ENABLE_HMAC = True           # sign tokens with HMAC to detect tampering
SECRET_KEY = b"week10-secret-key-change-in-prod"

# Logging
LOG_FILE = "quantum_messenger.log"
