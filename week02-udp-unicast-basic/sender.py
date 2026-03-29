import socket
from config import HOST, PORT

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send message to receiver (no connect() needed!)
message = "Hello via UDP"
sock.sendto(message.encode(), (HOST, PORT))
print("[SENDER] Message sent")

# Sender does NOT wait for reply — fire and forget
sock.close()
