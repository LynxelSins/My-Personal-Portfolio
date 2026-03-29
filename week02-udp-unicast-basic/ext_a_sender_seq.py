"""
Extension A: Sequence Numbers — Sender
Sends 5 messages tagged with sequence IDs.
"""
import socket
import time
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(5):
    message = f"{i}|Message {i}"
    sock.sendto(message.encode(), (HOST, PORT))
    print(f"[SENDER-A] Sent seq={i}")
    time.sleep(0.1)  # small delay so receiver can process

sock.close()
print("[SENDER-A] All messages sent.")
