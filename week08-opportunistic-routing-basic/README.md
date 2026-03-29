# Week 08 — Opportunistic Routing (Basic Lab)

## Overview
This lab demonstrates **opportunistic routing** in a delay-tolerant network (DTN).  
Each node maintains a **delivery probability table** and forwards messages only when a peer's probability exceeds a threshold.

---

## Directory Structure
```
week08-opportunistic-routing-basic/
├── README.md
├── config.py           ← Shared configuration (ports, threshold, interval)
├── delivery_table.py   ← Delivery probability table implementation
├── node.py             ← Main node logic (server + forwarding loop)
└── docs/
    └── run_instructions.md
```

---

## Quick Start

### 1. Clone the repo
```bash
git clone <repo-url>
cd week08-opportunistic-routing-basic
```

### 2. Run multiple nodes in separate terminals

**Terminal 1 — Node A (port 9000, peers: 9001, 9002)**
```bash
python node.py
```

**Terminal 2 — Node B (port 9001)**
```bash
# Edit config.py: BASE_PORT = 9001, PEER_PORTS = [9000, 9002]
python node.py
```

**Terminal 3 — Node C (port 9002)**
```bash
# Edit config.py: BASE_PORT = 9002, PEER_PORTS = [9000, 9001]
python node.py
```

---

## Key Concepts

| Concept | Description |
|---|---|
| **Delivery Probability** | How likely a node can reach the destination |
| **Threshold** | Only forward if probability > `FORWARD_THRESHOLD` (default 0.5) |
| **Message Queue** | Store messages when no suitable peer is available |
| **Opportunistic Forward** | Forward when a "good" encounter occurs |

---

## Expected Behavior
- Messages are sent **only** to peers with probability ≥ threshold
- If a peer is unreachable, the message is **queued**
- Every `UPDATE_INTERVAL` seconds, queued messages are retried
- Successful delivery removes the message from the queue

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Ignoring delivery probabilities | Messages forwarded blindly — defeats the purpose |
| Not queuing failed messages | Packets are lost permanently |
| Blocking I/O in main thread | Node can't receive while forwarding |

---

## Extension Branches

| Branch | Description |
|---|---|
| `ext/dynamic-probability` | Update probabilities based on encounter history |
| `ext/message-ttl` | Messages expire after a time window |
| `ext/logging-stats` | Track delivery attempts, successes, and failures |
