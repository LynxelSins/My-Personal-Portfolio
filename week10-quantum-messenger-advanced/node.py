# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, UPDATE_INTERVAL
from token import Token

token_queue = []
queue_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Step 2: Send a token to a peer
# ---------------------------------------------------------------------------
def send_token(peer_port, token):
    """
    Transmit the token's message to a peer.
    Note: we send the raw message string — the receiving node wraps it
    in a new Token object and must read it exactly once.
    """
    # Guard: don't forward a token that is already consumed or expired
    if token.read or token.is_expired():
        print(f"[NODE {BASE_PORT}] Token {token.token_id} not forwardable: {token.status()}")
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        # Encode token_id alongside message so receiver can track provenance
        payload = f"{token.token_id}|{token.message}"
        s.sendall(payload.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] → Sent token {token.token_id} to port {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] ✗ Failed to reach port {peer_port}")
        return False

# ---------------------------------------------------------------------------
# Step 3: Forwarding loop with one-time-read enforcement
# ---------------------------------------------------------------------------
def forward_loop():
    """
    Each cycle:
      1. Purge expired or already-consumed tokens from queue
      2. Attempt to forward remaining tokens to peers
      3. Remove successfully forwarded tokens
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        with queue_lock:
            # Purge invalid tokens
            before = len(token_queue)
            stale = [t for t in token_queue if t.read or t.is_expired()]
            for t in stale:
                token_queue.remove(t)
                print(f"[NODE {BASE_PORT}] 🗑 Purged token {t.token_id}: {t.status()}")
            if stale:
                print(f"[NODE {BASE_PORT}] Purged {len(stale)}/{before} token(s)")

            # Forward remaining tokens
            for token in token_queue[:]:
                for peer in PEER_PORTS:
                    if send_token(peer, token):
                        token_queue.remove(token)
                        break  # Token forwarded — do not clone to other peers
                else:
                    print(f"[NODE {BASE_PORT}] Token {token.token_id} still queued")

# ---------------------------------------------------------------------------
# Step 4: Server — receive incoming tokens
# ---------------------------------------------------------------------------
def handle_connection(conn, addr):
    """
    Receive a raw payload, construct a fresh Token, and read it exactly once.
    If the read succeeds, queue the token for potential re-forwarding.
    """
    try:
        data = conn.recv(BUFFER_SIZE).decode()
        # Unpack token_id|message format
        if "|" in data:
            origin_id, message = data.split("|", 1)
        else:
            origin_id, message = "unknown", data

        token = Token(message)
        print(f"[NODE {BASE_PORT}] ← Received token (origin={origin_id}) from {addr[0]}:{addr[1]}")

        content = token.read_token()   # Collapse — one-time read
        if content:
            print(f"[NODE {BASE_PORT}] 📨 Message: '{content}'")
            # Optionally re-queue for multi-hop forwarding
            # (students can enable this for Extension B)
            # with queue_lock:
            #     token_queue.append(Token(content))
        else:
            print(f"[NODE {BASE_PORT}] Token invalid — discarded")
    except Exception as e:
        print(f"[NODE {BASE_PORT}] ERROR: {e}")
    finally:
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

    # Create and queue the initial token
    initial_token = Token(f"Quantum token from node {BASE_PORT}")
    print(f"[NODE {BASE_PORT}] Created: {initial_token}")
    with queue_lock:
        token_queue.append(initial_token)

    print(f"[NODE {BASE_PORT}] Running — token expiry={initial_token.expiry}s, "
          f"forward interval={UPDATE_INTERVAL}s\n")

    # Keep alive
    while True:
        time.sleep(1)
