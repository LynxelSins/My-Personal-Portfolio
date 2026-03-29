"""
node.py — Decentralized Chat Overlay Node
Week 05 Advanced Lab

Features:
  - Dynamic peer discovery (share peer tables)
  - Message forwarding (no central server)
  - Heartbeat-based liveness detection
  - Graceful shutdown with BYE broadcast

Usage:
  python node.py <node_id> [seed_peer_id ...]

Examples:
  python node.py 1                  — standalone node (waits for others)
  python node.py 2 1                — node 2, connect to node 1 first
  python node.py 3 1 2              — node 3, knows about 1 and 2

Commands in REPL:
  peers                   — show known peers
  send <id> <message>     — send direct or routed message
  discover <id>           — request peer table from a peer
  quit                    — graceful shutdown
"""
import socket
import threading
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import HOST, BASE_PORT, BUFFER_SIZE, CONNECT_TIMEOUT, HEARTBEAT_INTERVAL
from peer_table import PeerTable
from router import Router
import utils.protocol as proto

# ── Setup ────────────────────────────────────────────────────────────────────

if len(sys.argv) < 2:
    print("Usage: python node.py <node_id> [seed_peer_ids...]")
    sys.exit(1)

node_id = int(sys.argv[1])
PORT = BASE_PORT + node_id

table = PeerTable(owner_id=node_id)

# ── Delivery callback ────────────────────────────────────────────────────────

def on_deliver(sender_id, message, hops):
    path = " → ".join(str(h) for h in hops + [node_id])
    print(f"\n[NODE {node_id}] ✉  From Peer {sender_id}: '{message}'")
    print(f"[NODE {node_id}]    Path: {path}")
    print(">> ", end="", flush=True)

router = Router(node_id, table, on_deliver)

# ── Send helper ──────────────────────────────────────────────────────────────

def send_packet(target_id: int, data: str) -> bool:
    port = table.get_port(target_id)
    if not port:
        return False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONNECT_TIMEOUT)
        sock.connect((HOST, port))
        sock.sendall(data.encode())
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

def broadcast(data: str):
    for pid in table.get_alive_ids():
        send_packet(pid, data)

# ── Listener ─────────────────────────────────────────────────────────────────

def handle_conn(conn, addr):
    try:
        data = conn.recv(BUFFER_SIZE)
        conn.close()
        if not data:
            return

        packet = proto.parse_packet(data)
        if not packet:
            return

        ptype = packet.get("type")
        sender = packet.get("sender_id")

        if ptype == proto.HELLO:
            table.add(sender, BASE_PORT + sender)
            table.mark_seen(sender)
            print(f"\n[NODE {node_id}] ✓ Peer {sender} joined")
            print(">> ", end="", flush=True)
            # Auto-share our table back
            my_peers = {str(k): v for k, v in table.get_all().items()}
            my_peers[str(node_id)] = PORT
            send_packet(sender, proto.peer_list_response(node_id, my_peers))

        elif ptype == proto.BYE:
            table.remove(sender)
            print(f"\n[NODE {node_id}] 👋 Peer {sender} left the network")
            print(">> ", end="", flush=True)

        elif ptype == proto.HEARTBEAT:
            table.mark_seen(sender)

        elif ptype == proto.PEER_LIST:
            foreign = packet.get("peers", {})
            table.merge(foreign)
            print(f"\n[NODE {node_id}] 🗂  Merged peer list from Peer {sender} ({len(foreign)} entries)")
            print(">> ", end="", flush=True)

        elif ptype == proto.DISCOVERY:
            my_peers = {str(k): v for k, v in table.get_all().items()}
            my_peers[str(node_id)] = PORT
            send_packet(sender, proto.peer_list_response(node_id, my_peers))

        elif ptype in (proto.MSG, proto.ROUTE):
            router.handle_incoming(packet)

    except Exception as e:
        print(f"[NODE {node_id}] Handler error: {e}")


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)
    print(f"[NODE {node_id}] Listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            threading.Thread(target=handle_conn, args=(conn, addr), daemon=True).start()
        except Exception:
            pass

# ── Heartbeat ─────────────────────────────────────────────────────────────────

def heartbeat_loop():
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        table.expire_stale(HEARTBEAT_INTERVAL * 2)
        hb = proto.heartbeat(node_id)
        for pid in table.get_alive_ids():
            ok = send_packet(pid, hb)
            if not ok:
                table.mark_dead(pid)

# ── Bootstrap ────────────────────────────────────────────────────────────────

def bootstrap(seed_ids: list[int]):
    """Connect to seed peers and request their peer tables."""
    for sid in seed_ids:
        port = BASE_PORT + sid
        table.add(sid, port)
        # Send HELLO
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECT_TIMEOUT)
            sock.connect((HOST, port))
            sock.sendall(proto.hello(node_id).encode())
            sock.close()
            print(f"[NODE {node_id}] → HELLO sent to Peer {sid}")
        except Exception:
            print(f"[NODE {node_id}] ✗ Could not reach seed Peer {sid}")

# ── Graceful shutdown ────────────────────────────────────────────────────────

def shutdown():
    print(f"\n[NODE {node_id}] Broadcasting BYE...")
    broadcast(proto.bye(node_id))
    time.sleep(0.3)
    print(f"[NODE {node_id}] Goodbye.")
    sys.exit(0)

# ── Main ──────────────────────────────────────────────────────────────────────

threading.Thread(target=listen, daemon=True).start()
threading.Thread(target=heartbeat_loop, daemon=True).start()

seed_ids = [int(x) for x in sys.argv[2:]]
if seed_ids:
    bootstrap(seed_ids)

print(f"\n[NODE {node_id}] Decentralized chat overlay active.")
print("Commands: peers | send <id> <msg> | discover <id> | quit\n")

while True:
    try:
        line = input(">> ").strip().split(maxsplit=2)
        if not line:
            continue

        if line[0] == "peers":
            print(table)

        elif line[0] == "send" and len(line) >= 3:
            target = int(line[1])
            msg = line[2]
            ok = router.send_direct(target, msg)
            if not ok:
                # Try routed delivery
                import json
                packet = json.loads(proto.chat(node_id, target, msg))
                ok = router.forward(packet)
            print(f"[NODE {node_id}] → Peer {target}: {'sent' if ok else 'no route found'}")

        elif line[0] == "discover" and len(line) >= 2:
            target = int(line[1])
            ok = send_packet(target, proto.discovery_request(node_id))
            print(f"[NODE {node_id}] Discovery request to Peer {target}: {'sent' if ok else 'failed'}")

        elif line[0] == "quit":
            shutdown()

        else:
            print("Commands: peers | send <id> <msg> | discover <id> | quit")

    except (ValueError, IndexError):
        print("Invalid format.")
    except KeyboardInterrupt:
        shutdown()
