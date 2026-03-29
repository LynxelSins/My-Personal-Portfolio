# node/node.py — Quantum-Secure Messenger Node (Advanced)
"""
Simulates a secure messaging node inspired by quantum principles:

  1. ONE-TIME-READ    — Each token can be consumed exactly once
  2. NO-CLONING       — Tokens are never duplicated across peers
  3. EPHEMERAL STATE  — Tokens expire; history prevents replay
  4. PROBABILISTIC    — Channel success is probabilistic (DELIVERY_PROBABILITY)
  5. TAMPER DETECTION — HMAC signature verified on receipt
  6. MULTI-HOP LIMIT  — Tokens discarded after MAX_HOPS traversals
"""

import socket
import threading
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE,
    UPDATE_INTERVAL, SHORT_EXPIRY
)
from node.token import QuantumToken
from node.state_manager import StateManager
from utils.logger import Logger

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
logger = Logger(BASE_PORT)
state = StateManager(BASE_PORT)
queue_lock = threading.Lock()
token_queue = []    # List[QuantumToken]


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------
def send_token(peer_port, token):
    """
    Attempt to send a QuantumToken to a peer.
    - Applies probabilistic collapse before the actual socket call
    - Increments the hop counter on success
    - Never forwards a token that is already consumed, expired, or at max hops
    """
    if not token.is_valid():
        logger.log(f"SKIP: token {token.token_id} is {token.status()}")
        return False

    # Probabilistic channel — quantum collapse simulation
    if not state.attempt_delivery():
        logger.log(
            f"COLLAPSE: token {token.token_id} → {peer_port} "
            f"(channel probability caused failure)"
        )
        logger.record("collapsed", token.token_id)
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        token.increment_hop()
        s.sendall(token.to_json().encode())
        s.close()
        logger.log(
            f"SENT: token {token.token_id} (hop {token.hops}) → {peer_port}"
        )
        logger.record("sent", token.token_id)
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        # Undo hop increment on connection failure
        token.hops = max(0, token.hops - 1)
        logger.log(f"UNREACHABLE: port {peer_port} — token {token.token_id} requeued")
        return False


# ---------------------------------------------------------------------------
# Receiving
# ---------------------------------------------------------------------------
def handle_connection(conn, addr):
    """
    Receive a JSON token, validate it (seen cache + HMAC + expiry),
    read it exactly once, then optionally re-queue for multi-hop forwarding.
    """
    try:
        raw = conn.recv(BUFFER_SIZE).decode()
        token = QuantumToken.from_json(raw)

        logger.log(
            f"RECEIVED: token {token.token_id} "
            f"(hop {token.hops}, priority={token.priority}) "
            f"from {addr[0]}:{addr[1]}"
        )
        logger.record("received", token.token_id)

        # Full validation pipeline
        if not state.validate_token(token, logger):
            if state.already_seen(token.token_id):
                logger.record("duplicates")
            elif not token.verify():
                logger.record("tampered")
            return

        # Mark as seen to prevent replay
        state.mark_seen(token.token_id)

        # One-time read — state collapse
        content = token.read_token()
        if content:
            logger.log(f"CONSUMED: '{content}' [{token.token_id}]")
            logger.record("consumed", token.token_id)

            # Multi-hop: re-queue as a new token if under hop limit
            if token.hops < 2:   # Allow one more hop
                new_token = QuantumToken(
                    message=content,
                    priority=token.priority,
                    hops=token.hops,
                    expiry=token.expiry,
                )
                with queue_lock:
                    token_queue.append(new_token)
                logger.log(
                    f"REQUEUED: new token {new_token.token_id} for multi-hop forwarding"
                )
        else:
            logger.log(f"READ FAILED: token {token.token_id} — {token.status()}")
            logger.record("expired", token.token_id)

    except ValueError as e:
        logger.log(f"PARSE ERROR: {e}")
    except Exception as e:
        logger.log(f"CONNECTION ERROR: {e}")
    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen(10)
    logger.log(f"SERVER: Listening on {HOST}:{BASE_PORT}")
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_connection, args=(conn, addr), daemon=True
            ).start()
        except Exception as e:
            logger.log(f"SERVER ERROR: {e}")


# ---------------------------------------------------------------------------
# Forwarding loop
# ---------------------------------------------------------------------------
def forward_loop():
    """
    Each cycle:
      1. Purge expired / invalid tokens
      2. Forward valid tokens to the best available peer (no-cloning: first success wins)
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        with queue_lock:
            # Purge stale tokens
            stale = [t for t in token_queue if not t.is_valid()]
            for t in stale:
                token_queue.remove(t)
                logger.log(f"PURGED: token {t.token_id} — {t.status()}")
                logger.record("expired", t.token_id)

            # Forward remaining tokens
            for token in token_queue[:]:
                for peer in PEER_PORTS:
                    if send_token(peer, token):
                        token_queue.remove(token)
                        break   # No-cloning: stop after first success


# ---------------------------------------------------------------------------
# Token factory helpers
# ---------------------------------------------------------------------------
def create_token(message, priority="normal", expiry=None):
    t = QuantumToken(message, priority=priority, expiry=expiry)
    logger.log(f"CREATED: {t}")
    logger.record("created", t.token_id)
    with queue_lock:
        token_queue.append(t)
    return t


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"\n🔐 Quantum Messenger Node {BASE_PORT} starting...\n")

    # Start server
    threading.Thread(target=start_server, daemon=True).start()

    # Start forwarding loop
    threading.Thread(target=forward_loop, daemon=True).start()

    time.sleep(0.5)

    # Create initial tokens with different priorities and expiry windows
    create_token(f"Standard message from node {BASE_PORT}", priority="normal")
    create_token(f"Ephemeral secret from node {BASE_PORT}", priority="ephemeral",
                 expiry=SHORT_EXPIRY)
    create_token(f"High-priority alert from node {BASE_PORT}", priority="high")

    print(f"\n[NODE {BASE_PORT}] Queue: {len(token_queue)} token(s) pending\n")

    # Periodic stats
    try:
        while True:
            time.sleep(UPDATE_INTERVAL * 3)
            state.print_stats()
            logger.print_stats()
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down...")
        state.print_stats()
        logger.print_stats()
        csv = logger.export_transitions()
        if csv:
            print(f"[NODE {BASE_PORT}] Transition log → {csv}")
