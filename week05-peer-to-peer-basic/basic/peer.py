"""
Basic P2P Peer Node
Usage: python peer.py <peer_id>
Example:
    Terminal 1: python peer.py 1   (listens on port 9001)
    Terminal 2: python peer.py 2   (listens on port 9002)
"""
import socket
import threading
import sys
from config import HOST, BASE_PORT, BUFFER_SIZE

if len(sys.argv) < 2:
    print("Usage: python peer.py <peer_id>")
    print("Example: python peer.py 1")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id


# ── Step 2: Listener Thread ──────────────────────────────────────────────────

def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            data = conn.recv(BUFFER_SIZE)
            if data:
                print(f"\n[PEER {peer_id}] ← From {addr}: {data.decode()}")
                print("Send to peer ID: ", end="", flush=True)
            conn.close()
        except Exception as e:
            print(f"[PEER {peer_id}] Listener error: {e}")


# ── Step 3: Sender Function ──────────────────────────────────────────────────

def send_message(target_peer_id, message):
    target_port = BASE_PORT + target_peer_id
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((HOST, target_port))
        sock.sendall(message.encode())
        sock.close()
        print(f"[PEER {peer_id}] → Sent to Peer {target_peer_id}: {message}")
    except ConnectionRefusedError:
        print(f"[PEER {peer_id}] ✗ Peer {target_peer_id} is not online (port {target_port} refused)")
    except socket.timeout:
        print(f"[PEER {peer_id}] ✗ Peer {target_peer_id} timed out")


# ── Step 4: Start listener + interactive sender ──────────────────────────────

threading.Thread(target=listen, daemon=True).start()

print(f"[PEER {peer_id}] Ready. Type a target peer ID and message to send.")
print("[PEER {0}] (Ctrl+C to quit)\n".format(peer_id))

while True:
    try:
        target = int(input("Send to peer ID: "))
        if target == peer_id:
            print(f"[PEER {peer_id}] ✗ Cannot send to yourself.")
            continue
        msg = input("Message: ")
        if msg.strip():
            send_message(target, msg)
        else:
            print("[PEER] Empty message skipped.")
    except ValueError:
        print("[PEER] Please enter a valid integer peer ID.")
    except KeyboardInterrupt:
        print(f"\n[PEER {peer_id}] Shutting down.")
        sys.exit(0)
