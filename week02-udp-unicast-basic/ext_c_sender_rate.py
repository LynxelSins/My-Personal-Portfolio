"""
Extension C: Rate Control — Sender
Sends 100 messages as fast as possible to observe receiver saturation.
Watch receiver terminal to see if any messages are dropped at OS level.
"""
import socket
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("[SENDER-C] Sending 100 messages at full speed...\n")

for i in range(100):
    message = f"Fast message {i}"
    sock.sendto(message.encode(), (HOST, PORT))
    # No delay — fire as fast as possible
    if (i + 1) % 10 == 0:
        print(f"[SENDER-C] Sent {i + 1}/100 messages")

sock.close()
print("\n[SENDER-C] Done. Check receiver — did it get all 100?")
