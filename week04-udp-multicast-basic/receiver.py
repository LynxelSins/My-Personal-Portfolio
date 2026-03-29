import socket
import struct
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

# Create UDP socket (IPPROTO_UDP for multicast)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the multicast PORT (not the group address!)
sock.bind(("", PORT))

# Join multicast group — this is the "subscribe" operation
# struct.pack("4sl", ...) converts IP to binary form for kernel
mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined multicast group {MULTICAST_GROUP}:{PORT}")
print("[RECEIVER] Waiting for messages... (Ctrl+C to stop)\n")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER] {addr} -> {data.decode()}")
    except KeyboardInterrupt:
        print("\n[RECEIVER] Leaving group and stopping.")
        break

sock.close()
