"""
Extension B: Multiple Groups
Receiver subscribes to 3 different multicast channels simultaneously.
Use ext_b_sender_group*.py to send to each group individually.
"""
import socket
import struct
from config import PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

# Join multiple groups (channels)
groups = ["224.1.1.1", "224.1.1.2", "224.1.1.3"]
for group in groups:
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f"[RECEIVER-B] Joined channel {group}")

print(f"\n[RECEIVER-B] Subscribed to {len(groups)} channels on port {PORT}")
print("[RECEIVER-B] Waiting for messages... (Ctrl+C to stop)\n")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER-B] From {addr}: {data.decode()}")
    except KeyboardInterrupt:
        print("\n[RECEIVER-B] Stopped.")
        break

sock.close()
