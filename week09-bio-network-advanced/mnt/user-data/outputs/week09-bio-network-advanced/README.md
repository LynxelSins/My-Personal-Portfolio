# Week 09 — Self-Healing Bio-Routing Network (Advanced Lab)

## Overview
This advanced lab simulates a **self-healing network** inspired by **Ant Colony Optimization (ACO)**.  
When a link fails, pheromone trails decay, ants explore alternatives, and the network converges to a new optimal path — automatically.

---

## Directory Structure
```
week09-bio-network-advanced/
├── README.md
├── config.py                    ← Pheromone params, failure timing, flow count
├── node/
│   ├── node.py                  ← Self-healing node (multi-flow + failure aware)
│   ├── pheromone_table.py       ← Advanced table: multi-hop + history export
│   └── encounter_simulator.py   ← Simulates random link failures & recoveries
└── utils/
    └── logger.py                ← Event log + stats + CSV pheromone history
```

---

## Advanced Concepts

| Concept | Description |
|---|---|
| **Self-healing** | Network re-routes around broken links automatically |
| **Multi-flow** | Multiple simultaneous message streams compete for paths |
| **Multi-hop pheromone** | Track pheromone to non-direct destinations via peers |
| **Pheromone history** | Export time-series data for visualisation (Extension C) |

---

## Quick Start

**Terminal 1 — Node A (port 10100)**
```bash
cd week09-bio-network-advanced
python -m node.node
```

**Terminal 2 — Node B (port 10101)**
Edit `config.py`: `BASE_PORT = 10101`, `PEER_PORTS = [10100, 10102]`
```bash
python -m node.node
```

**Terminal 3 — Node C (port 10102)**
Edit `config.py`: `BASE_PORT = 10102`, `PEER_PORTS = [10100, 10101]`
```bash
python -m node.node
```

---

## Self-Healing in Action

```
[12:00:20] LINK FAILURE: Node 10100 ↔ 10101 broken ✂
[12:00:20] FAILED: msg#5 → 10101
[12:00:24] CYCLE: 1 viable path(s) — queue=1       ← reroutes via 10102
[12:00:24] SENT: msg#5 (flow 2) → 10102
[12:00:40] LINK RECOVERY: Node 10100 ↔ 10101 restored 🔗
[12:00:44] SELF-HEAL: Path from 10101 re-established 🔄
```

---

## Output Files
| File | Contents |
|---|---|
| `node<PORT>_bio_network.log` | Full timestamped event log |
| `node<PORT>_pheromone_history.csv` | Time-series pheromone data (on Ctrl+C) |

---

## Real-World Mapping

| Simulation | Real World |
|---|---|
| Link failure | Cable cut, node crash, radio interference |
| Pheromone decay | Route table aging / TTL |
| Multi-flow | Concurrent data streams from sensors |
| Self-heal | Dynamic re-routing without central controller |

---

## Forward Application Hooks
- **Week 10:** Replace pheromone model with quantum-inspired probability amplitudes
- **Capstone:** Full bio-routing simulator with live network topology visualisation
