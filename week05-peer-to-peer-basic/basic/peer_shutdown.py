"""
Extension 3: Graceful Shutdown
Peers notify each other before going offline.
Observers remove the departed peer from their known list.
Usage: python peer_shutdown.py <peer_id> [known_peer_ids...]
Example: python peer_shutdown.py 1 2 3
"""
import socket
import threading
import sys
import json
from config import HOST, BASE_PORT, BUFFER_SIZE

if len(sys.argv) < 2:
    print("Usage: python peer_shutdown.py <peer_id> [known_peer_ids...]")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

# Pre-populate known peers from command line args
known_peers = {}
for pid_str in sys.argv[2:]:
    pid = int(pid_str)
    known_peers[pid] = BASE_PORT + pid

known_peers_lock = threading.Lock()
running = True


def send_packet(target_peer_id, packet: dict) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((HOST, BASE_PORT + target_peer_id))
        sock.sendall(json.dumps(packet).encode())
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False


def broadcast(packet: dict):
    """Send packet to all known peers."""
    with known_peers_lock:
        targets = list(known_peers.keys())
    for pid in targets:
        send_packet(pid, packet)


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while running:
        try:
            sock.settimeout(1)
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                continue

            data = conn.recv(BUFFER_SIZE)
            conn.close()
            if not data:
                continue

            packet = json.loads(data.decode())
            ptype = packet.get("type")

            if ptype == "HELLO":
                pid = packet["peer_id"]
                with known_peers_lock:
                    known_peers[pid] = BASE_PORT + pid
                print(f"\n[PEER {peer_id}] ✓ Peer {pid} is online")
                print(">> ", end="", flush=True)

            elif ptype == "MSG":
                print(f"\n[PEER {peer_id}] ← Peer {packet['from']}: {packet['message']}")
                print(">> ", end="", flush=True)

            elif ptype == "BYE":
                pid = packet["peer_id"]
                with known_peers_lock:
                    known_peers.pop(pid, None)
                print(f"\n[PEER {peer_id}] 👋 Peer {pid} has left the network (removed from list)")
                print(">> ", end="", flush=True)

        except Exception:
            pass

    sock.close()


def graceful_shutdown():
    """Notify all known peers before exiting."""
    global running
    running = False
    bye_packet = {"type": "BYE", "peer_id": peer_id}
    with known_peers_lock:
        targets = list(known_peers.keys())
    for pid in targets:
        ok = send_packet(pid, bye_packet)
        print(f"[PEER {peer_id}] 👋 Notified Peer {pid}: {'OK' if ok else 'offline'}")
    print(f"[PEER {peer_id}] Shutdown complete.")
    sys.exit(0)


# Start listener
threading.Thread(target=listen, daemon=True).start()

# Announce self to known peers
hello = {"type": "HELLO", "peer_id": peer_id}
broadcast(hello)

print(f"\n[PEER {peer_id}] Online. Known peers: {list(known_peers.keys())}")
print("Commands: peers | send <id> <msg> | quit\n")

while True:
    try:
        line = input(">> ").strip().split(maxsplit=2)
        if not line:
            continue

        if line[0] == "peers":
            with known_peers_lock:
                if known_peers:
                    for pid, port in known_peers.items():
                        print(f"  Peer {pid} → port {port}")
                else:
                    print("  No known peers.")

        elif line[0] == "send" and len(line) >= 3:
            target = int(line[1])
            msg = line[2]
            packet = {"type": "MSG", "from": peer_id, "message": msg}
            ok = send_packet(target, packet)
            print(f"[PEER {peer_id}] → Peer {target}: {'sent' if ok else 'FAILED'}")

        elif line[0] == "quit":
            graceful_shutdown()

        else:
            print("Commands: peers | send <id> <msg> | quit")

    except (ValueError, IndexError):
        print("Invalid format.")
    except KeyboardInterrupt:
        graceful_shutdown()
