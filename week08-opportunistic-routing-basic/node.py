# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, FORWARD_THRESHOLD, UPDATE_INTERVAL
from delivery_table import DeliveryTable

delivery_table = DeliveryTable()
message_queue = []
queue_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Step 2: Send a message to a peer
# ---------------------------------------------------------------------------
def send_message(peer_port, message):
    """Attempt to send a message to a peer. Returns True on success."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] ✓ Sent: '{message}' → port {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] ✗ Failed to reach port {peer_port}")
        return False

# ---------------------------------------------------------------------------
# Step 3: Opportunistic Forwarding Loop
# ---------------------------------------------------------------------------
def forward_loop():
    """Periodically check queue and forward messages to best candidates."""
    while True:
        time.sleep(UPDATE_INTERVAL)
        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)

        if not candidates:
            print(f"[NODE {BASE_PORT}] No candidates above threshold {FORWARD_THRESHOLD}")
            continue

        with queue_lock:
            for msg in message_queue[:]:
                forwarded = False
                for peer in candidates:
                    if send_message(peer, msg):
                        message_queue.remove(msg)
                        forwarded = True
                        break  # Stop after first successful forward
                if not forwarded:
                    print(f"[NODE {BASE_PORT}] Message still queued: '{msg}'")

# ---------------------------------------------------------------------------
# Step 4: Server to receive incoming messages
# ---------------------------------------------------------------------------
def handle_connection(conn, addr):
    """Handle an incoming connection from another node."""
    data = conn.recv(BUFFER_SIZE).decode()
    print(f"[NODE {BASE_PORT}] ← Received: '{data}' from {addr[0]}:{addr[1]}")
    with queue_lock:
        message_queue.append(data)
    conn.close()

def start_server():
    """Listen for incoming messages from other nodes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening on {HOST}:{BASE_PORT}...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

# ---------------------------------------------------------------------------
# Step 5: Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Start server and forwarding threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialize delivery probabilities (precomputed or from config)
    for peer in PEER_PORTS:
        delivery_table.update_probability(peer, 0.6)

    delivery_table.display()

    # Try sending initial messages; queue if peer is unavailable
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Peer {peer} unreachable — storing in queue")
            with queue_lock:
                message_queue.append(msg)

    print(f"\n[NODE {BASE_PORT}] Running. Queue size: {len(message_queue)}")
    print(f"[NODE {BASE_PORT}] Forwarding every {UPDATE_INTERVAL}s if prob > {FORWARD_THRESHOLD}\n")

    # Keep main thread alive
    while True:
        time.sleep(1)
