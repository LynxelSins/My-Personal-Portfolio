"""
Extension B: Multiple Groups — Sender
Sends one message to each of the 3 multicast groups.
Run ext_b_receiver_multigroup.py to receive from all channels.
"""
import socket
from config import PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

groups = {
    "224.1.1.1": "News channel",
    "224.1.1.2": "Sports channel",
    "224.1.1.3": "Weather channel",
}

for group, channel_name in groups.items():
    message = f"[{channel_name}] Hello from {group}"
    sock.sendto(message.encode(), (group, PORT))
    print(f"[SENDER-B] Sent to {group}: {message}")

sock.close()
print("\n[SENDER-B] Done. Receiver should show all 3 messages.")
