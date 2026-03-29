"""
Extension B: Manual ACK — Sender with Retry
Sender waits for ACK after each message; retries on timeout.
This is UDP behaving like a reliable protocol — you built mini-TCP!
"""
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)  # 2-second timeout waiting for ACK

message = "Message requiring ACK"
max_retries = 3
success = False

for attempt in range(1, max_retries + 1):
    sock.sendto(message.encode(), (HOST, PORT))
    print(f"[SENDER-B] Sent (attempt {attempt}/{max_retries}): {message}")

    try:
        ack, addr = sock.recvfrom(BUFFER_SIZE)
        if ack.decode() == "ACK":
            print(f"[SENDER-B] ✓ ACK received from {addr}!")
            success = True
            break
    except socket.timeout:
        print(f"[SENDER-B] ✗ No ACK — timeout. Retrying...")

if not success:
    print("[SENDER-B] ✗ Failed to deliver after max retries.")

sock.close()
