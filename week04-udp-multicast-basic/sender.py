import socket
from config import MULTICAST_GROUP, PORT, TTL

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Set TTL to limit scope (1 = stay on LAN, 255 = internet)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

# Send to multicast group address — no join needed for sender!
message = "MULTICAST: Hello subscribers"
sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))

print(f"[SENDER] Multicast sent to {MULTICAST_GROUP}:{PORT}")
print(f"[SENDER] Message: {message}")
sock.close()
