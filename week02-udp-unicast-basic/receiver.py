import socket
from config import HOST, PORT, BUFFER_SIZE

# Create UDP socket (SOCK_DGRAM = UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to local address:port (no listen() needed!)
sock.bind((HOST, PORT))
print(f"[RECEIVER] Listening on {HOST}:{PORT}")
print("[RECEIVER] Waiting for datagrams... (Ctrl+C to stop)\n")

# Wait for datagrams indefinitely
while True:
    try:
        # recvfrom() BLOCKS until a datagram arrives
        # Returns BOTH data and sender address
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode()
        print(f"[RECEIVER] From {addr}: {message}")
    except KeyboardInterrupt:
        print("\n[RECEIVER] Stopped.")
        break

sock.close()
