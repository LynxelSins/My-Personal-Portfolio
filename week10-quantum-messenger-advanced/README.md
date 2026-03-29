# Week 10 — Quantum-Inspired Network (Basic Lab)

## Overview
This lab simulates **quantum-inspired token routing** where each token can be read **exactly once**.  
Reading a token "collapses" its state — just like measuring a quantum state collapses the superposition.  
Expired or already-read tokens are automatically discarded.

---

## Directory Structure
```
week10-quantum-network-basic/
├── README.md
├── config.py       ← Ports, expiry, update interval
├── token.py        ← One-time-read Token class
├── node.py         ← Node: server + forwarding loop + expiry purge
└── docs/
    └── run_instructions.md
```

---

## Key Concepts

| Quantum Principle | Network Simulation |
|---|---|
| **No-cloning theorem** | A token cannot be duplicated or re-sent once consumed |
| **State collapse** | Reading a token marks it permanently consumed |
| **Decoherence / expiry** | Tokens become invalid after `TOKEN_EXPIRY` seconds |
| **Superposition** | Token exists in "unread" state until the first observation |

---

## Quick Start

**Terminal 1 — Node A (port 11000)**
```bash
python node.py
```

**Terminal 2 — Node B (port 11001)**
```bash
# Edit config.py: BASE_PORT = 11001, PEER_PORTS = [11000, 11002]
python node.py
```

**Terminal 3 — Node C (port 11002)**
```bash
# Edit config.py: BASE_PORT = 11002, PEER_PORTS = [11000, 11001]
python node.py
```

---

## Expected Output

```
[NODE 11000] Created: Token(id=a3f1b2c4, status=active (10.0s remaining), ...)
[NODE 11000] → Sent token a3f1b2c4 to port 11001
[NODE 11001] ← Received token (origin=a3f1b2c4) from 127.0.0.1:11000
[TOKEN a3f1b2c4] ✓ Consumed after 0.12s — state collapsed
[NODE 11001] 📨 Message: 'Quantum token from node 11000'
```

Attempting to re-read the same token:
```
[TOKEN a3f1b2c4] ✗ Already consumed (collapsed state)
```

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Ignoring token read state | Violates one-time-read — same message delivered multiple times |
| No expiry check | Stale tokens circulate indefinitely |
| Cloning the token to multiple peers | Breaks the no-cloning guarantee |

---

## Extension Branches

| Branch | Description |
|---|---|
| `ext/expiry-management` | Configurable per-token expiry + active cleanup thread |
| `ext/multi-hop` | Re-queue consumed content as new token; track hop history |
| `ext/logging-viz` | Log token state transitions; visualize collapse over network |
