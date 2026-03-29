# Week 10 — Quantum-Secure Messenger (Advanced Lab)

## Overview
This advanced lab simulates a **quantum-inspired secure messaging system**.  
Every quantum principle from the basic lab is extended with real security mechanics and probabilistic network modelling.

---

## Directory Structure
```
week10-quantum-messenger-advanced/
├── README.md
├── config.py                  ← Token params, delivery probability, HMAC key
├── node/
│   ├── node.py                ← Main messenger node (multi-token, multi-hop)
│   ├── token.py               ← QuantumToken: HMAC signing, hop limit, serialisation
│   └── state_manager.py       ← Seen-token cache + probabilistic delivery model
└── utils/
    └── logger.py              ← Event log + stats + CSV transition export
```

---

## Quantum Principles → Implementation

| Quantum Concept | Implementation |
|---|---|
| **No-cloning theorem** | `break` after first successful peer send |
| **State collapse** | `read_token()` sets `self.read = True` permanently |
| **Decoherence** | `TOKEN_EXPIRY` — token becomes invalid over time |
| **Measurement probability** | `DELIVERY_PROBABILITY` — channel is probabilistic |
| **Entanglement / provenance** | HMAC signature ties token to its origin |
| **No-replay** | Seen-token LRU cache blocks re-delivered token IDs |

---

## Quick Start

**Terminal 1 — Node A (port 11100)**
```bash
cd week10-quantum-messenger-advanced
python -m node.node
```

**Terminal 2 — Node B (port 11101)**
Edit `config.py`: `BASE_PORT = 11101`, `PEER_PORTS = [11100, 11102]`
```bash
python -m node.node
```

**Terminal 3 — Node C (port 11102)**
Edit `config.py`: `BASE_PORT = 11102`, `PEER_PORTS = [11100, 11101]`
```bash
python -m node.node
```

---

## Sample Output

```
🔐 Quantum Messenger Node 11100 starting...

[12:01:00] CREATED: QuantumToken(id=3a9f1b2c, priority=normal, status=active (15.0s left, hop 0/3))
[12:01:00] CREATED: QuantumToken(id=7d2e4f8a, priority=ephemeral, status=active (5.0s left, hop 0/3))
[12:01:04] SENT: token 3a9f1b2c (hop 1) → 11101
[12:01:04] RECEIVED: token 3a9f1b2c (hop 1) from 127.0.0.1:11100
[12:01:04] CONSUMED: 'Standard message from node 11100' [3a9f1b2c]
[12:01:08] COLLAPSE: token 7d2e4f8a → 11102 (channel probability caused failure)
[12:01:08] PURGED: token 7d2e4f8a — expired
```

---

## Output Files

| File | Contents |
|---|---|
| `node<PORT>_quantum_messenger.log` | Full event log |
| `node<PORT>_transitions.csv` | Token state transitions (on Ctrl+C) |

---

## Real-World Mapping

| Simulation | Real World |
|---|---|
| One-time-read | One-time pad / QKD key consumption |
| HMAC signature | Quantum authentication protocol |
| Probabilistic delivery | Quantum channel noise / photon loss |
| Seen-token cache | Replay attack prevention |
| Token expiry | Key freshness / forward secrecy |

---

## Forward Application Hooks
- **Capstone:** Combine with Week 09 bio-routing — pheromone selects paths, quantum tokens secure the payload
- **Optional:** Replace HMAC with asymmetric signatures (RSA/ECDSA) for full PKI simulation
