"""
router.py
Handles message forwarding logic for the P2P overlay.
No central server — each node routes independently using its peer table.
"""
import socket
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import HOST, CONNECT_TIMEOUT, BUFFER_SIZE, MAX_HOPS
from utils.protocol import parse_packet, make_packet, MSG, ROUTE


class Router:
    def __init__(self, node_id: int, peer_table, on_deliver):
        """
        node_id    : this node's ID
        peer_table : PeerTable instance
        on_deliver : callback(sender_id, message, hops) when message reaches destination
        """
        self.node_id = node_id
        self.peer_table = peer_table
        self.on_deliver = on_deliver

    def _send_raw(self, target_port: int, data: str) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECT_TIMEOUT)
            sock.connect((HOST, target_port))
            sock.sendall(data.encode())
            sock.close()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

    def send_direct(self, destination: int, message: str) -> bool:
        """Send message directly to destination peer."""
        port = self.peer_table.get_port(destination)
        if not port:
            return False

        packet = make_packet(
            MSG, self.node_id,
            destination=destination,
            message=message,
            hops=[self.node_id],
        )
        return self._send_raw(port, packet)

    def forward(self, packet: dict) -> bool:
        """
        Forward a packet toward its destination.
        Tries direct path first; if unknown, relays via any alive peer.
        """
        destination = packet.get("destination")
        hops = packet.get("hops", [])

        # Loop detection
        if self.node_id in hops:
            print(f"[ROUTER {self.node_id}] ⚠ Loop detected — dropping packet")
            return False

        if len(hops) >= MAX_HOPS:
            print(f"[ROUTER {self.node_id}] ⚠ Max hops ({MAX_HOPS}) reached — dropping")
            return False

        hops.append(self.node_id)
        packet["hops"] = hops

        import json
        raw = json.dumps(packet)

        # Try direct route
        port = self.peer_table.get_port(destination)
        if port:
            ok = self._send_raw(port, raw)
            if ok:
                return True

        # Try relay via any alive peer (excluding visited hops)
        for pid in self.peer_table.get_alive_ids():
            if pid not in hops and pid != destination:
                relay_port = self.peer_table.get_port(pid)
                if relay_port:
                    ok = self._send_raw(relay_port, raw)
                    if ok:
                        print(f"[ROUTER {self.node_id}] ↪ Relaying via Peer {pid}")
                        return True

        print(f"[ROUTER {self.node_id}] ✗ No route to Peer {destination}")
        return False

    def handle_incoming(self, packet: dict):
        """Process an incoming MSG/ROUTE packet."""
        destination = packet.get("destination")
        sender = packet.get("sender_id")
        message = packet.get("message", "")
        hops = packet.get("hops", [])

        if destination == self.node_id:
            # We are the final destination
            self.on_deliver(sender, message, hops)
        else:
            # Forward it
            self.forward(packet)
