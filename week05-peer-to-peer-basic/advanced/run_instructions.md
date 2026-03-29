# Run Instructions — Week 05 P2P

## Basic Lab

### Basic Peer (peer.py)
```powershell
# Terminal 1
cd basic
python peer.py 1

# Terminal 2
cd basic
python peer.py 2
```
Then type in either terminal: peer ID → message.

---

### Extension 1: Peer List (peer_list.py)
```powershell
# Terminal 1
python peer_list.py 1

# Terminal 2
python peer_list.py 2

# In Terminal 1, type:
add 2
send 2 Hello from peer 1!
peers
```

---

### Extension 2: Message Relay (peer_relay.py)
3-peer chain: Peer1 ←→ Peer2 ←→ Peer3 (Peer1 and Peer3 don't know each other directly)
```powershell
# Terminal 1
python peer_relay.py 1

# Terminal 2
python peer_relay.py 2

# Terminal 3
python peer_relay.py 3

# In Terminal 1:
send 2 Hello direct to 2
relay 3 via 2 Hello to 3 via 2!   ← routes through peer 2
```

---

### Extension 3: Graceful Shutdown (peer_shutdown.py)
```powershell
# Terminal 1 (knows about peer 2)
python peer_shutdown.py 1 2

# Terminal 2 (knows about peer 1)
python peer_shutdown.py 2 1

# In Terminal 1, type: quit
# Terminal 2 will print: Peer 1 has left the network
```

---

## Advanced Lab (Decentralized Overlay)

```powershell
cd advanced

# Terminal 1 — standalone seed node
python node.py 1

# Terminal 2 — connect to node 1
python node.py 2 1

# Terminal 3 — connect to node 1 (discovers node 2 automatically)
python node.py 3 1
```

### Advanced Commands
```
peers              — show current peer table (alive/dead status)
send 2 Hello!      — send to peer 2 (direct or auto-routed)
discover 3         — request peer table from peer 3
quit               — broadcast BYE and exit gracefully
```

### Port Assignments
| Node ID | Port (Basic) | Port (Advanced) |
|---------|-------------|----------------|
| 1       | 9001        | 9101            |
| 2       | 9002        | 9102            |
| 3       | 9003        | 9103            |
| N       | 9000+N      | 9100+N          |
