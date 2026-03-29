import socket
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from config import BUFFER_SIZE, TIMEOUT
from logger import info, warn, error

def handle_client(conn: socket.socket, addr: tuple):
    """
    Handle a single client connection — chat session loop.
    Client can type messages; server echoes back with timestamp ACK.
    Session ends when client sends 'quit' or disconnects.
    """
    info(f"New client connected: {addr}")
    conn.settimeout(TIMEOUT)

    try:
        # Send welcome message
        welcome = (
            "=== Helpdesk Chat Server ===\n"
            "Type your message and press Enter.\n"
            "Type 'quit' to disconnect.\n"
            "============================\n"
        )
        conn.sendall(welcome.encode())

        while True:
            try:
                data = conn.recv(BUFFER_SIZE)

                # Client disconnected cleanly
                if not data:
                    info(f"Client {addr} disconnected (empty data)")
                    break

                message = data.decode().strip()

                # Validate: reject empty messages
                if not message:
                    warn(f"Client {addr} sent empty message — rejected")
                    conn.sendall("[SERVER] Empty message rejected.\n".encode())
                    continue

                # Validate: enforce max length
                if len(message) > 256:
                    warn(f"Client {addr} sent oversized message ({len(message)} chars) — rejected")
                    conn.sendall("[SERVER] Message too long (max 256 chars).\n".encode())
                    continue

                info(f"Message from {addr}: {message}")

                # Handle quit command
                if message.lower() == "quit":
                    conn.sendall("[SERVER] Goodbye! Closing connection.\n".encode())
                    info(f"Client {addr} requested quit")
                    break

                # Echo back with ACK
                import datetime
                ts = datetime.datetime.now().strftime("%H:%M:%S")
                reply = f"[{ts}] ACK: {message}\n"
                conn.sendall(reply.encode())

            except socket.timeout:
                warn(f"Client {addr} timed out after {TIMEOUT}s")
                conn.sendall("[SERVER] Session timed out. Disconnecting.\n".encode())
                break

    except ConnectionResetError:
        warn(f"Client {addr} forcibly disconnected")
    except Exception as e:
        error(f"Unexpected error with client {addr}: {e}")
    finally:
        conn.close()
        info(f"Connection with {addr} closed")