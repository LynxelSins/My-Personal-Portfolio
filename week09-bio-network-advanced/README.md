# Week 09 — Bio-Inspired Routing (Basic Lab)

## Overview
This lab implements **bio-inspired routing** using a pheromone-based model derived from **Ant Colony Optimization (ACO)**.  
Nodes reinforce successful paths and let unused paths evaporate — routing emerges naturally over time.

---

## Directory Structure
```
week09-bio-routing-basic/
├── README.md
├── config.py            ← Ports, pheromone parameters, thresholds
├── pheromone_table.py   ← Pheromone trail management (reinforce / decay)
├── node.py              ← Node with bio-inspired forwarding loop
└── docs/
    └── run_instructions.md
```

---

## Key Concepts

| Concept | Ant Colony Analogy | Network Role |
|---|---|---|
| **Pheromone** | Chemical trail ants leave | Path quality score |
| **Reinforcement** | Ant deposits more pheromone | Success increases path score |
| **Decay** | Trail evaporates over time | Stale paths fade away |
| **Threshold** | Minimum scent to follow | Minimum score to forward |

---

## Quick Start

**Terminal 1 — Node A (port 10000)**
```bash
python node.py
```

**Terminal 2 — Node B (port 10001)**
```bash
# Edit config.py: BASE_PORT = 10001, PEER_PORTS = [10000, 10002]
python node.py
```

**Terminal 3 — Node C (port 10002)**
```bash
# Edit config.py: BASE_PORT = 10002, PEER_PORTS = [10000, 10001]
python node.py
```

---

## Expected Behaviour
1. Nodes start with equal pheromone on all paths
2. Successful deliveries **reinforce** the used path
3. Every `UPDATE_INTERVAL` seconds, all paths **decay**
4. Over time, the best-performing path accumulates more pheromone
5. Failed paths are penalized and eventually drop below threshold

---

## Parameters to Experiment With

| Parameter | Default | Effect |
|---|---|---|
| `DECAY_FACTOR` | 0.9 | Lower = faster forgetting |
| `REINFORCEMENT` | 0.1 | Higher = stronger learning |
| `FORWARD_THRESHOLD` | 0.2 | Higher = more selective routing |
| `UPDATE_INTERVAL` | 5s | Lower = faster adaptation |

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Not decaying pheromones | Old paths dominate indefinitely — no adaptation |
| Ignoring failed transmissions | Reinforcement logic breaks — bad paths persist |
| Blocking I/O in main thread | Node cannot receive while forwarding |

---

## Extension Branches

| Branch | Description |
|---|---|
| `ext/dynamic-learning` | Round-trip success updates pheromone + congestion avoidance |
| `ext/multi-hop` | Pheromone table stores paths beyond direct neighbors |
| `ext/logging-viz` | Plot pheromone table evolution over time |
