"""
Extension C: Rate Control — Receiver
Counts received messages and reports total at the end.
Compare with sender's sent count to observe packet loss.
"""
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[RECEIVER-C] Listening on {HOST}:{PORT} (Rate mode)")
print("[RECEIVER-C] Counting messages... (Ctrl+C to see results)\n")

count = 0

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        count += 1
        message = data.decode()
        print(f"[RECEIVER-C] #{count:03d} | {message}")
    except KeyboardInterrupt:
        print(f"\n[RECEIVER-C] Total received: {count}/100")
        if count < 100:
            print(f"[RECEIVER-C] ⚠ Lost: {100 - count} messages — UDP dropped them silently!")
        else:
            print("[RECEIVER-C] ✓ All messages received (lucky loopback!)")
        break

sock.close()
