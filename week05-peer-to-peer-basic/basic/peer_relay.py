"""
Extension 2: Message Relay (Hop-Based Routing)
Peers can forward messages to other peers they know.
Observe how messages travel hop-by-hop across the network.

Usage: python peer_relay.py <peer_id>
Example topology: Peer1 → Peer2 → Peer3 (Peer1 can reach Peer3 via Peer2)

Commands:
  route <target_id> via <hop_id> <message>  — send via relay
  send <target_id> <message>                — direct send
"""
import socket
import threading
import sys
import json
from config import HOST, BASE_PORT, BUFFER_SIZE

if len(sys.argv) < 2:
    print("Usage: python peer_relay.py <peer_id>")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id


def send_raw(target_peer_id, packet: dict) -> bool:
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
            conn.close()
            if not data:
                continue

            packet = json.loads(data.decode())
            ptype = packet.get("type")
            origin = packet.get("origin", "?")
            destination = packet.get("destination", peer_id)
            hops = packet.get("hops", [])
            message = packet.get("message", "")

            hops.append(peer_id)

            if destination == peer_id:
                # Final destination
                hop_path = " → ".join(str(h) for h in hops)
                print(f"\n[PEER {peer_id}] ← MSG from Peer {origin}: '{message}'")
                print(f"[PEER {peer_id}]   Path: {hop_path}")
            else:
                # Relay forward
                packet["hops"] = hops
                ok = send_raw(destination, packet)
                hop_path = " → ".join(str(h) for h in hops)
                if ok:
                    print(f"\n[PEER {peer_id}] ↪ Relayed to Peer {destination} | Path so far: {hop_path}")
                else:
                    print(f"\n[PEER {peer_id}] ✗ Cannot relay to Peer {destination} (offline)")

            print(">> ", end="", flush=True)

        except Exception as e:
            print(f"[PEER {peer_id}] Error: {e}")


threading.Thread(target=listen, daemon=True).start()

print(f"\n[PEER {peer_id}] Online. Relay mode active.")
print("Commands:")
print("  send <to> <msg>               — direct message")
print("  relay <to> via <hop> <msg>    — route through another peer")
print("  quit\n")

while True:
    try:
        line = input(">> ").strip()
        if not line:
            continue
        parts = line.split(maxsplit=4)

        if parts[0] == "send" and len(parts) >= 3:
            target = int(parts[1])
            msg = " ".join(parts[2:])
            packet = {
                "type": "MSG",
                "origin": peer_id,
                "destination": target,
                "message": msg,
                "hops": []
            }
            ok = send_raw(target, packet)
            print(f"[PEER {peer_id}] → Direct to Peer {target}: {'OK' if ok else 'FAILED'}")

        elif parts[0] == "relay" and len(parts) >= 5 and parts[2] == "via":
            target = int(parts[1])
            hop = int(parts[3])
            msg = " ".join(parts[4:])
            packet = {
                "type": "MSG",
                "origin": peer_id,
                "destination": target,
                "message": msg,
                "hops": []
            }
            ok = send_raw(hop, packet)
            print(f"[PEER {peer_id}] → Via Peer {hop} → Peer {target}: {'OK' if ok else 'FAILED (hop offline)'}")

        elif parts[0] == "quit":
            sys.exit(0)

        else:
            print("Unknown command.")

    except (ValueError, IndexError):
        print("Invalid format.")
    except KeyboardInterrupt:
        print(f"\n[PEER {peer_id}] Shutting down.")
        sys.exit(0)
