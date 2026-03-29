"""
utils/protocol.py
Defines all message types and packet builders for the P2P overlay.
"""
import json
import time

# ── Message Types ────────────────────────────────────────────────────────────
HELLO     = "HELLO"      # Peer announces itself
BYE       = "BYE"        # Peer leaving gracefully
MSG       = "MSG"        # Chat message (direct or routed)
ROUTE     = "ROUTE"      # Routed message (hop-based)
DISCOVERY = "DISCOVERY"  # Request peer table from another peer
PEER_LIST = "PEER_LIST"  # Response: share known peers
HEARTBEAT = "HEARTBEAT"  # Liveness ping
ACK       = "ACK"        # Generic acknowledgement


def make_packet(msg_type: str, sender_id: int, **kwargs) -> str:
    """Build a JSON-encoded packet."""
    packet = {
        "type": msg_type,
        "sender_id": sender_id,
        "timestamp": time.time(),
        **kwargs
    }
    return json.dumps(packet)


def parse_packet(raw: bytes) -> dict | None:
    """Parse raw bytes into a packet dict. Returns None on failure."""
    try:
        return json.loads(raw.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


# ── Packet Builders ──────────────────────────────────────────────────────────

def hello(sender_id: int) -> str:
    return make_packet(HELLO, sender_id)

def bye(sender_id: int) -> str:
    return make_packet(BYE, sender_id)

def chat(sender_id: int, destination: int, message: str, hops: list = None) -> str:
    return make_packet(
        MSG, sender_id,
        destination=destination,
        message=message,
        hops=hops or [],
    )

def route(sender_id: int, destination: int, message: str, hops: list) -> str:
    return make_packet(
        ROUTE, sender_id,
        destination=destination,
        message=message,
        hops=hops,
    )

def discovery_request(sender_id: int) -> str:
    return make_packet(DISCOVERY, sender_id)

def peer_list_response(sender_id: int, peers: dict) -> str:
    return make_packet(PEER_LIST, sender_id, peers=peers)

def heartbeat(sender_id: int) -> str:
    return make_packet(HEARTBEAT, sender_id)

def ack(sender_id: int, ref_type: str) -> str:
    return make_packet(ACK, sender_id, ref_type=ref_type)
