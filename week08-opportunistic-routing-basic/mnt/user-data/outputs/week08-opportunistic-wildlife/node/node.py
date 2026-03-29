# node/node.py — Wildlife Tracking Network Node (Advanced)
"""
Simulates a mobile wildlife sensor node that:
  1. Listens for incoming sensor data from other animals
  2. Maintains a delivery probability table updated by encounters
  3. Forwards stored messages opportunistically when paths cross
  4. Expires messages that have exceeded their TTL
"""

import socket
import threading
import time
import sys
import os

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE,
    FORWARD_THRESHOLD, UPDATE_INTERVAL, MESSAGE_TTL
)
from node.delivery_table import DeliveryTable
from node.encounter_simulator import EncounterSimulator
from utils.logger import Logger

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
delivery_table = DeliveryTable()
logger = Logger(BASE_PORT)
queue_lock = threading.Lock()

# Each message: {"data": str, "created_at": float}
message_queue = []


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------
def make_message(data):
    return {"data": data, "created_at": time.time()}


def is_expired(msg):
    return (time.time() - msg["created_at"]) > MESSAGE_TTL


def purge_expired():
    """Remove messages that have exceeded their TTL."""
    with queue_lock:
        expired = [m for m in message_queue if is_expired(m)]
        for m in expired:
            message_queue.remove(m)
            logger.record_expired()
            logger.log(f"TTL EXPIRED: '{m['data']}'")
    return len(expired)


# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
def send_message(peer_port, message_data):
    """Attempt to send message data to a peer. Returns True on success."""
    logger.record_attempt()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message_data.encode())
        s.close()
        logger.record_success()
        delivery_table.record_delivery_success(peer_port)
        logger.log(f"SENT: '{message_data}' → {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        logger.record_failure()
        delivery_table.record_delivery_failure(peer_port)
        logger.log(f"FAILED: Could not reach {peer_port}")
        return False


def handle_connection(conn, addr):
    """Handle incoming message from another node."""
    try:
        data = conn.recv(BUFFER_SIZE).decode()
        logger.log(f"RECEIVED: '{data}' from {addr[0]}:{addr[1]}")
        # Store received message for potential re-forwarding
        with queue_lock:
            message_queue.append(make_message(data))
    except Exception as e:
        logger.log(f"ERROR receiving message: {e}")
    finally:
        conn.close()


def start_server():
    """Listen for incoming connections from other wildlife nodes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen(5)
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
    Every UPDATE_INTERVAL seconds:
      1. Purge expired messages
      2. Find peers above the delivery threshold
      3. Opportunistically forward queued messages
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        # Expire old messages
        n_expired = purge_expired()
        if n_expired:
            logger.log(f"Purged {n_expired} expired message(s)")

        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)
        logger.log(f"FORWARD CHECK: {len(candidates)} candidate(s) above threshold {FORWARD_THRESHOLD}")

        if not candidates:
            continue

        with queue_lock:
            for msg in message_queue[:]:
                if is_expired(msg):
                    continue
                for peer in candidates:
                    if send_message(peer, msg["data"]):
                        message_queue.remove(msg)
                        break  # Delivered — no need to try other peers
                else:
                    logger.record_queued()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"\n🐾 Wildlife Node {BASE_PORT} starting up...\n")

    # Start server thread
    threading.Thread(target=start_server, daemon=True).start()

    # Start encounter simulator
    simulator = EncounterSimulator(delivery_table, logger, BASE_PORT)
    simulator.run()

    # Start forwarding loop
    threading.Thread(target=forward_loop, daemon=True).start()

    # Seed some initial messages (sensor readings)
    time.sleep(1)
    sensor_data = [
        f"GPS:{BASE_PORT}:lat=15.87,lon=100.99",
        f"TEMP:{BASE_PORT}:37.2C",
        f"HEARTRATE:{BASE_PORT}:82bpm",
    ]
    for reading in sensor_data:
        msg = make_message(reading)
        for peer in PEER_PORTS:
            if not send_message(peer, reading):
                with queue_lock:
                    message_queue.append(msg)
                logger.log(f"QUEUED: '{reading}' (peer {peer} unavailable)")
                break

    # Periodic stats display
    try:
        while True:
            time.sleep(15)
            delivery_table.display()
            logger.print_stats()
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down...")
        delivery_table.display()
        logger.print_stats()
