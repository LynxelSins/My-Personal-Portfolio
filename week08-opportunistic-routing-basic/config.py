# config.py
HOST = "127.0.0.1"
BASE_PORT = 9000
PEER_PORTS = [9001, 9002]  # Example peers
BUFFER_SIZE = 1024
FORWARD_THRESHOLD = 0.5  # Forward if delivery probability > threshold
UPDATE_INTERVAL = 5      # seconds
