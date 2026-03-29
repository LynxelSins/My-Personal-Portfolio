"""
Test 3: Non-Member Doesn't Receive — Selectivity Proof
This receiver deliberately skips IP_ADD_MEMBERSHIP.
Result: It will receive nothing even when sender is active.
"""
import socket
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

# Deliberately skip: sock.setsockopt(..., IP_ADD_MEMBERSHIP, ...)
print(f"[RECEIVER (NO JOIN)] Bound to port {PORT} — but NOT joined group {MULTICAST_GROUP}")
print("[RECEIVER (NO JOIN)] Should receive NOTHING from multicast sender.\n")

sock.settimeout(5)

try:
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"[RECEIVER (NO JOIN)] Unexpectedly got from {addr}: {data.decode()}")
        except socket.timeout:
            print("[RECEIVER (NO JOIN)] 5s timeout — no data received (as expected!)")
except KeyboardInterrupt:
    print("\n[RECEIVER (NO JOIN)] Stopped.")

sock.close()
