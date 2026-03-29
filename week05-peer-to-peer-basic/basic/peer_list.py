"""
Extension 1: Peer List Management
Each peer maintains a list of known peers.
On startup, register yourself. Use 'peers' command to see who's online.
Usage: python peer_list.py <peer_id>
"""
import socket
import threading
import sys
import json
from config import HOST, BASE_PORT, BUFFER_SIZE

if len(sys.argv) < 2:
    print("Usage: python peer_list.py <peer_id>")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

# Known peers: {peer_id: port}
known_peers = {}
known_peers_lock = threading.Lock()


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
            if not data:
                conn.close()
                continue

            try:
                packet = json.loads(data.decode())
                ptype = packet.get("type")

                if ptype == "HELLO":
                    # Peer announced itself
                    pid = packet["peer_id"]
                    with known_peers_lock:
                        known_peers[pid] = BASE_PORT + pid
                    print(f"\n[PEER {peer_id}] ✓ Peer {pid} joined the network")
                    print(">> ", end="", flush=True)

                elif ptype == "MSG":
                    sender = packet["from"]
                    msg = packet["message"]
                    print(f"\n[PEER {peer_id}] ← Peer {sender}: {msg}")
                    print(">> ", end="", flush=True)

            except json.JSONDecodeError:
                # Fallback: plain text
                print(f"\n[PEER {peer_id}] ← {addr}: {data.decode()}")
                print(">> ", end="", flush=True)

            conn.close()
        except Exception as e:
            print(f"[PEER {peer_id}] Listener error: {e}")


def send_packet(target_peer_id, packet: dict):
    target_port = BASE_PORT + target_peer_id
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((HOST, target_port))
        sock.sendall(json.dumps(packet).encode())
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False


def announce_self():
    """Broadcast HELLO to all known peers."""
    packet = {"type": "HELLO", "peer_id": peer_id}
    with known_peers_lock:
        targets = list(known_peers.keys())
    for pid in targets:
        send_packet(pid, packet)


def probe_peer(target_id):
    """Check if a peer is online and add to known_peers."""
    packet = {"type": "HELLO", "peer_id": peer_id}
    success = send_packet(target_id, packet)
    if success:
        with known_peers_lock:
            known_peers[target_id] = BASE_PORT + target_id
        print(f"[PEER {peer_id}] ✓ Peer {target_id} is online and added.")
    else:
        print(f"[PEER {peer_id}] ✗ Peer {target_id} is not reachable.")


# Start listener
threading.Thread(target=listen, daemon=True).start()

print(f"\n[PEER {peer_id}] Online at port {PORT}")
print("Commands:")
print("  peers          — list known peers")
print("  add <id>       — probe and add a peer")
print("  send <id> <msg>— send message to peer")
print("  quit           — exit\n")

while True:
    try:
        cmd = input(">> ").strip().split(maxsplit=2)
        if not cmd:
            continue

        if cmd[0] == "peers":
            with known_peers_lock:
                if known_peers:
                    for pid, port in known_peers.items():
                        print(f"  Peer {pid} → port {port}")
                else:
                    print("  No known peers yet. Use 'add <id>' to find peers.")

        elif cmd[0] == "add" and len(cmd) >= 2:
            probe_peer(int(cmd[1]))

        elif cmd[0] == "send" and len(cmd) >= 3:
            target = int(cmd[1])
            message = cmd[2]
            packet = {"type": "MSG", "from": peer_id, "message": message}
            ok = send_packet(target, packet)
            if ok:
                print(f"[PEER {peer_id}] → Sent to Peer {target}: {message}")
            else:
                print(f"[PEER {peer_id}] ✗ Peer {target} not reachable.")

        elif cmd[0] == "quit":
            print(f"[PEER {peer_id}] Goodbye.")
            sys.exit(0)

        else:
            print("Unknown command. Try: peers | add <id> | send <id> <msg> | quit")

    except (ValueError, IndexError):
        print("Invalid command format.")
    except KeyboardInterrupt:
        print(f"\n[PEER {peer_id}] Shutting down.")
        sys.exit(0)
