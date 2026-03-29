# node/node.py — Self-Healing Bio-Routing Network Node (Advanced)
"""
Simulates a network node that:
  1. Routes messages along high-pheromone paths
  2. Reinforces successful paths and penalizes failures
  3. Decays pheromone each cycle so stale paths fade
  4. Adapts automatically when links fail (self-healing)
  5. Handles multiple simultaneous message flows
  6. Exports pheromone history for visualization
"""

import socket
import threading
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE,
    INITIAL_PHEROMONE, REINFORCEMENT, FORWARD_THRESHOLD,
    UPDATE_INTERVAL, NUM_FLOWS
)
from node.pheromone_table import PheromoneTable
from node.encounter_simulator import LinkFailureSimulator
from utils.logger import Logger

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
pheromone_table = PheromoneTable(BASE_PORT)
logger = Logger(BASE_PORT)
queue_lock = threading.Lock()

# Each message: {"id": int, "flow": int, "data": str, "hops": int}
message_queue = []
_msg_id = 0


def next_id():
    global _msg_id
    _msg_id += 1
    return _msg_id


# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
def send_message(peer_port, msg, failure_sim=None):
    """
    Send a message to a peer.
    Respects simulated link failures from the LinkFailureSimulator.
    Returns True on success.
    """
    # Check if this link is simulated as broken
    if failure_sim and failure_sim.is_blocked(peer_port):
        logger.log(
            f"BLOCKED: msg#{msg['id']} → {peer_port} (simulated failure)"
        )
        pheromone_table.penalize(peer_port)
        logger.record_failed()
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        payload = f"[flow={msg['flow']}|id={msg['id']}|hops={msg['hops']}] {msg['data']}"
        s.sendall(payload.encode())
        s.close()

        pheromone_table.reinforce(peer_port, REINFORCEMENT)
        logger.record_sent()
        logger.log(f"SENT: msg#{msg['id']} (flow {msg['flow']}) → {peer_port}")
        return True

    except (ConnectionRefusedError, socket.timeout, OSError):
        pheromone_table.penalize(peer_port)
        logger.record_failed()
        logger.log(f"FAILED: msg#{msg['id']} → {peer_port}")
        return False


def handle_connection(conn, addr):
    """Process an incoming message and check for self-healing opportunity."""
    try:
        raw = conn.recv(BUFFER_SIZE).decode()
        logger.log(f"RECEIVED: '{raw}' from {addr[0]}:{addr[1]}")

        # Parse hop count to detect multi-hop routing
        hops = 0
        if "hops=" in raw:
            try:
                hops = int(raw.split("hops=")[1].split("]")[0]) + 1
            except (IndexError, ValueError):
                pass

        # Track that this path is working — record as a self-heal if we
        # previously thought the sender was unreachable
        sender_port = addr[1]
        old_pher = pheromone_table.get_pheromone(sender_port)
        if old_pher < FORWARD_THRESHOLD:
            logger.record_healed()
            logger.log(f"SELF-HEAL: Path from {sender_port} re-established 🔄")

        with queue_lock:
            msg_id = next_id()
            message_queue.append({
                "id": msg_id, "flow": 0, "data": raw, "hops": hops
            })
    except Exception as e:
        logger.log(f"ERROR in handle_connection: {e}")
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
# Forwarding loop — bio-inspired self-healing
# ---------------------------------------------------------------------------
def forward_loop(failure_sim):
    """
    Each cycle:
      1. Decay pheromone trails (evaporation)
      2. Find best candidates above threshold
      3. Forward queued messages along best paths
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        pheromone_table.decay()
        logger.record_decay()

        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)
        logger.log(
            f"CYCLE: {len(candidates)} viable path(s) — "
            f"queue={len(message_queue)}"
        )

        if not candidates:
            logger.log("No paths above threshold — waiting for network recovery")
            continue

        with queue_lock:
            for msg in message_queue[:]:
                delivered = False
                for peer in candidates:
                    if send_message(peer, msg, failure_sim):
                        message_queue.remove(msg)
                        delivered = True
                        break
                if not delivered:
                    logger.record_queued()


# ---------------------------------------------------------------------------
# Multi-flow message generator
# ---------------------------------------------------------------------------
def generate_flows():
    """
    Simulate NUM_FLOWS simultaneous data streams.
    Each flow sends a message every UPDATE_INTERVAL * 2 seconds.
    """
    def flow_worker(flow_id):
        seq = 0
        while True:
            time.sleep(UPDATE_INTERVAL * 2)
            seq += 1
            msg = {
                "id": next_id(),
                "flow": flow_id,
                "data": f"Flow-{flow_id} packet #{seq} from node {BASE_PORT}",
                "hops": 0,
            }
            # Try direct delivery first; queue if it fails
            candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)
            sent = False
            for peer in candidates:
                if send_message(peer, msg):
                    sent = True
                    break
            if not sent:
                with queue_lock:
                    message_queue.append(msg)
                logger.log(f"QUEUED: Flow-{flow_id} packet #{seq}")

    for fid in range(1, NUM_FLOWS + 1):
        threading.Thread(target=flow_worker, args=(fid,), daemon=True).start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"\n🐜 Bio-Routing Self-Healing Node {BASE_PORT} starting...\n")

    # Initialise pheromone trails
    for peer in PEER_PORTS:
        pheromone_table.reinforce(peer, INITIAL_PHEROMONE)

    pheromone_table.display()

    # Start server
    threading.Thread(target=start_server, daemon=True).start()

    # Start link failure simulator
    failure_sim = LinkFailureSimulator(pheromone_table, logger, BASE_PORT)
    failure_sim.run()

    # Start forwarding loop
    threading.Thread(
        target=forward_loop, args=(failure_sim,), daemon=True
    ).start()

    # Start multi-flow generators
    generate_flows()

    # Initial probe messages
    time.sleep(1)
    for peer in PEER_PORTS:
        probe = {"id": next_id(), "flow": 0,
                 "data": f"PROBE from node {BASE_PORT}", "hops": 0}
        if not send_message(peer, probe, failure_sim):
            with queue_lock:
                message_queue.append(probe)

    # Periodic stats + table display
    try:
        while True:
            time.sleep(UPDATE_INTERVAL * 3)
            pheromone_table.display()
            logger.print_stats()
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down...")
        pheromone_table.display()
        logger.print_stats()
        # Export pheromone history for Extension C visualisation
        csv_path = logger.export_pheromone_history(
            pheromone_table.get_history_summary()
        )
        print(f"[NODE {BASE_PORT}] Pheromone history saved → {csv_path}")
