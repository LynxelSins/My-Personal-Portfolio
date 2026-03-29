"""
peer_table.py
Thread-safe peer table for dynamic peer discovery and liveness tracking.
"""
import threading
import time


class PeerTable:
    def __init__(self, owner_id: int):
        self.owner_id = owner_id
        self._peers: dict[int, dict] = {}  # {peer_id: {port, last_seen, alive}}
        self._lock = threading.RLock()

    def add(self, peer_id: int, port: int):
        """Add or refresh a peer."""
        with self._lock:
            self._peers[peer_id] = {
                "port": port,
                "last_seen": time.time(),
                "alive": True,
            }

    def remove(self, peer_id: int):
        """Remove a peer (graceful leave)."""
        with self._lock:
            self._peers.pop(peer_id, None)

    def mark_seen(self, peer_id: int):
        """Update last-seen timestamp for a peer."""
        with self._lock:
            if peer_id in self._peers:
                self._peers[peer_id]["last_seen"] = time.time()
                self._peers[peer_id]["alive"] = True

    def mark_dead(self, peer_id: int):
        """Mark a peer as unreachable."""
        with self._lock:
            if peer_id in self._peers:
                self._peers[peer_id]["alive"] = False

    def get_port(self, peer_id: int) -> int | None:
        with self._lock:
            entry = self._peers.get(peer_id)
            return entry["port"] if entry else None

    def get_all(self) -> dict:
        """Return a snapshot: {peer_id: port} for all alive peers."""
        with self._lock:
            return {
                pid: info["port"]
                for pid, info in self._peers.items()
                if info["alive"]
            }

    def get_alive_ids(self) -> list[int]:
        with self._lock:
            return [pid for pid, info in self._peers.items() if info["alive"]]

    def merge(self, foreign_peers: dict):
        """
        Merge a foreign peer table into ours (dynamic discovery).
        foreign_peers: {str(peer_id): port}
        """
        with self._lock:
            for pid_str, port in foreign_peers.items():
                pid = int(pid_str)
                if pid != self.owner_id and pid not in self._peers:
                    self._peers[pid] = {
                        "port": port,
                        "last_seen": 0,  # not yet confirmed alive
                        "alive": True,
                    }

    def expire_stale(self, timeout_seconds: float):
        """Mark peers not seen within timeout as dead."""
        now = time.time()
        with self._lock:
            for pid, info in self._peers.items():
                if info["alive"] and (now - info["last_seen"]) > timeout_seconds:
                    info["alive"] = False

    def __len__(self):
        with self._lock:
            return len(self._peers)

    def __repr__(self):
        with self._lock:
            lines = [f"PeerTable (owner={self.owner_id}):"]
            for pid, info in self._peers.items():
                status = "✓" if info["alive"] else "✗"
                lines.append(f"  {status} Peer {pid} → port {info['port']}")
            return "\n".join(lines)
