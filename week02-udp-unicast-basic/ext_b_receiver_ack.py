"""
Extension B: Manual ACK — Receiver
Receives a message and sends back "ACK" to the sender.
"""
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[RECEIVER-B] Listening on {HOST}:{PORT} (ACK mode)")
print("[RECEIVER-B] Waiting for message... (Ctrl+C to stop)\n")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode()
        print(f"[RECEIVER-B] ✓ Received from {addr}: {message}")

        # Send ACK back to sender
        sock.sendto(b"ACK", addr)
        print(f"[RECEIVER-B] → ACK sent to {addr}")

    except KeyboardInterrupt:
        print("\n[RECEIVER-B] Stopped.")
        break

sock.close()
