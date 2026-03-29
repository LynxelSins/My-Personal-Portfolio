"""
Mini Chat Server — Advanced Lab
Handles multiple clients sequentially (or via threads if THREADED=True).
"""

import socket
import threading
import sys
import os

# Add both current dir and parent dir to path
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from config import HOST, PORT, BUFFER_SIZE, MAX_CLIENTS
from logger import info, warn, error
from client_handler import handle_client

THREADED = True  # Set False for sequential (blocking) mode

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
    except OSError as e:
        error(f"Bind failed: {e} — is port {PORT} already in use?")
        sys.exit(1)

    server_socket.listen(MAX_CLIENTS)
    info(f"Helpdesk Chat Server started on {HOST}:{PORT}")
    info(f"Mode: {'Threaded (concurrent)' if THREADED else 'Sequential (blocking)'}")
    info("Press Ctrl+C to stop the server.")

    client_count = 0

    try:
        while True:
            info("Waiting for next client...")
            conn, addr = server_socket.accept()
            client_count += 1
            info(f"Client #{client_count} accepted from {addr}")

            if THREADED:
                t = threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True,
                    name=f"Client-{client_count}"
                )
                t.start()
                info(f"Thread {t.name} started")
            else:
                # Sequential: blocks until this client is done
                handle_client(conn, addr)

    except KeyboardInterrupt:
        info("Server shutting down (KeyboardInterrupt)")
    finally:
        server_socket.close()
        info("Server socket closed. Total clients served: " + str(client_count))

if __name__ == "__main__":
    run_server()