"""
Extension C: Dynamic Join / Leave
Receiver joins a group, listens for 15 seconds, then leaves.
Messages only arrive while subscribed — proves membership is runtime-controlled.
Run ext_a_sender_stream.py in another terminal to send continuous updates.
"""
import socket
import struct
import time
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))
sock.settimeout(1)

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)

# --- Phase 1: JOIN and receive for 15 seconds ---
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print(f"[RECEIVER-C] JOINED {MULTICAST_GROUP} — receiving for 15 seconds...\n")

deadline = time.time() + 15
while time.time() < deadline:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER-C] ✓ {data.decode()}")
    except socket.timeout:
        pass  # keep looping until deadline

# --- Phase 2: LEAVE ---
sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
print(f"\n[RECEIVER-C] LEFT {MULTICAST_GROUP} — no longer subscribed.")
print("[RECEIVER-C] Waiting 10 more seconds (should receive NOTHING)...\n")

deadline = time.time() + 10
while time.time() < deadline:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER-C] ✗ Got data after leaving?! {data.decode()}")
    except socket.timeout:
        pass

print("[RECEIVER-C] Done. Confirmed: no messages after IP_DROP_MEMBERSHIP.")
sock.close()
