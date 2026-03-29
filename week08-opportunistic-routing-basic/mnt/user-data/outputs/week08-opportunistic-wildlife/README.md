# Week 08 — Wildlife Tracking Network (Advanced Lab)

## Overview
This advanced lab simulates **mobile wildlife sensor nodes** that communicate opportunistically when animals' paths cross.  
It extends the basic lab with:
- 🐾 **Encounter-based probability updates** (adaptive, history-driven)
- ⏱ **Message TTL** (messages expire if not delivered in time)
- 📊 **Logging & statistics** (track attempts, successes, failures, expiry)

---

## Directory Structure
```
week08-opportunistic-wildlife/
├── README.md
├── config.py                    ← Network + simulator configuration
├── node/
│   ├── node.py                  ← Main wildlife node (server + forwarder)
│   ├── delivery_table.py        ← Adaptive delivery probability table
│   └── encounter_simulator.py   ← Simulates random animal encounters
└── utils/
    └── logger.py                ← Event logging + statistics
```

---

## Concepts Introduced

| Concept | Description |
|---|---|
| **Encounter-based routing** | Probability increases each time nodes "meet" |
| **Probability aging** | Probabilities decay when nodes drift apart |
| **Message TTL** | Messages are discarded after `MESSAGE_TTL` seconds |
| **Adaptive forwarding** | Routing decisions improve over time from history |

---

## Quick Start

### Terminal 1 — Animal Node A (port 9100)
```bash
cd week08-opportunistic-wildlife
python -m node.node
```

### Terminal 2 — Animal Node B (port 9101)
Edit `config.py`: `BASE_PORT = 9101`, `PEER_PORTS = [9100, 9102]`
```bash
python -m node.node
```

### Terminal 3 — Animal Node C (port 9102)
Edit `config.py`: `BASE_PORT = 9102`, `PEER_PORTS = [9100, 9101]`
```bash
python -m node.node
```

---

## Real-World Mapping

| Simulation Element | Real-World Equivalent |
|---|---|
| Node | Animal with GPS/sensor collar |
| Encounter | Two animals entering radio range |
| Message queue | Sensor readings buffered on collar |
| Delivery probability | Historical contact frequency |
| TTL | Battery / storage limit on collar |

---

## Forward Application Hooks
- **Week 9:** Replace probability updates with reinforcement learning
- **Capstone:** Simulate full delay-tolerant sensor network (DTN) with map visualization

---

## Log Files
Each node writes to `node<PORT>_wildlife_network.log`.  
Review these after a run to analyze routing behavior.
