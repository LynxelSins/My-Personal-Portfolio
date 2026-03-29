# node.py
import socket
import threading
import time
from config import (
    HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE,
    FORWARD_THRESHOLD, UPDATE_INTERVAL,
    REINFORCEMENT, INITIAL_PHEROMONE
)
from pheromone_table import PheromoneTable

pheromone_table = PheromoneTable()
message_queue = []
queue_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Step 2: Send message with pheromone reinforcement
# ---------------------------------------------------------------------------
def send_message(peer_port, message):
    """
    Attempt to deliver a message to a peer.
    On success → reinforce the pheromone trail.
    On failure → penalize the trail slightly.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] ✓ Sent: '{message}' → port {peer_port}")
        pheromone_table.reinforce(peer_port, REINFORCEMENT)  # Reinforce successful path
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] ✗ Failed to reach port {peer_port}")
        pheromone_table.penalize(peer_port)
        return False

# ---------------------------------------------------------------------------
# Step 3: Forwarding loop with decay
# ---------------------------------------------------------------------------
def forward_loop():
    """
    Each cycle:
      1. Decay all pheromone trails (evaporation)
      2. Find best candidates above threshold
      3. Attempt to forward queued messages
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        pheromone_table.decay()
        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)

        if not candidates:
            print(f"[NODE {BASE_PORT}] No paths above threshold {FORWARD_THRESHOLD}")
            continue

        print(f"[NODE {BASE_PORT}] Forwarding to candidates: {candidates}")

        with queue_lock:
            for msg in message_queue[:]:
                for peer in candidates:
                    if send_message(peer, msg):
                        message_queue.remove(msg)
                        break  # Delivered — stop trying other peers
                else:
                    print(f"[NODE {BASE_PORT}] Still queued: '{msg}'")

# ---------------------------------------------------------------------------
# Step 4: Server — receive incoming messages
# ---------------------------------------------------------------------------
def handle_connection(conn, addr):
    data = conn.recv(BUFFER_SIZE).decode()
    print(f"[NODE {BASE_PORT}] ← Received: '{data}' from {addr[0]}:{addr[1]}")
    with queue_lock:
        message_queue.append(data)
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen(5)
    print(f"[NODE {BASE_PORT}] Listening on {HOST}:{BASE_PORT}...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

# ---------------------------------------------------------------------------
# Step 5: Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialize pheromone trails for all peers
    for peer in PEER_PORTS:
        pheromone_table.reinforce(peer, INITIAL_PHEROMONE)

    pheromone_table.display()

    # Initial message attempts — queue if peer unavailable
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Peer {peer} unreachable — queuing message")
            with queue_lock:
                message_queue.append(msg)

    print(f"\n[NODE {BASE_PORT}] Running. Queue: {len(message_queue)} message(s)")
    print(f"[NODE {BASE_PORT}] Decay={pheromone_table.table}, Threshold={FORWARD_THRESHOLD}\n")

    # Keep alive + periodic table display
    cycle = 0
    while True:
        time.sleep(UPDATE_INTERVAL)
        cycle += 1
        if cycle % 2 == 0:
            pheromone_table.display()
