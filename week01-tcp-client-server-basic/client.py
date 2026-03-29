"""
Chat Client — Advanced Lab
Interactive terminal client for the Mini Chat Server.
"""

import socket
import threading
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from config import HOST, PORT, BUFFER_SIZE

def receive_messages(sock: socket.socket):
    """Background thread: continuously print incoming server messages."""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("\n[CLIENT] Server closed the connection.")
                os._exit(0)
            print(data.decode(), end="", flush=True)
        except (ConnectionResetError, OSError):
            print("\n[CLIENT] Disconnected from server.")
            os._exit(0)

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"[CLIENT] Connected to {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"[CLIENT] ERROR: Could not connect to {HOST}:{PORT}. Is the server running?")
        sys.exit(1)

    # Start background thread for receiving
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    recv_thread.start()

    # Main loop: read user input and send
    try:
        while True:
            message = input()
            if not message.strip():
                continue  # Don't send blank lines
            client_socket.sendall(message.encode())
            if message.strip().lower() == "quit":
                break
    except (KeyboardInterrupt, EOFError):
        print("\n[CLIENT] Interrupted. Disconnecting...")
        try:
            client_socket.sendall("quit".encode())
        except Exception:
            pass
    finally:
        client_socket.close()
        print("[CLIENT] Connection closed.")

if __name__ == "__main__":
    run_client()