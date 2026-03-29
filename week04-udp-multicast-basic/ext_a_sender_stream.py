"""
Extension A: Periodic Multicast Stream
Sender broadcasts updates every 2 seconds indefinitely.
Run multiple receivers to see all of them receive each update.
"""
import socket
import time
from config import MULTICAST_GROUP, PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

print(f"[SENDER-A] Streaming to {MULTICAST_GROUP}:{PORT} every 2 seconds...")
print("[SENDER-A] Press Ctrl+C to stop.\n")

count = 0
try:
    while True:
        message = f"Update #{count} @ {time.strftime('%H:%M:%S')}"
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
        print(f"[SENDER-A] Sent: {message}")
        count += 1
        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n[SENDER-A] Stopped. Total sent: {count}")

sock.close()
