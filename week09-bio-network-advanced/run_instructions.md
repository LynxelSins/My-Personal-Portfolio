# Run Instructions — Week 09 Basic Lab

## Prerequisites
- Python 3.8+
- Standard library only — no pip installs required

---

## Running the Lab

### Step 1: Open 3 separate terminals

### Step 2: Configure ports for each terminal

| Terminal | BASE_PORT | PEER_PORTS       |
|----------|-----------|------------------|
| 1        | 10000     | [10001, 10002]   |
| 2        | 10001     | [10000, 10002]   |
| 3        | 10002     | [10000, 10001]   |

Edit `config.py` before each run, or copy it to `config_10001.py` etc.

### Step 3: Start each node
```bash
python node.py
```

---

## Test Scenarios

### Scenario A: Pheromone Reinforcement
Start all 3 nodes → watch pheromone values rise on active paths.

### Scenario B: Decay in Action
Start all nodes → kill one → observe pheromone drop below threshold after several decay cycles.

### Scenario C: Path Recovery (Self-Healing)
Kill node B → pheromone on that path decays → restart node B → watch pheromone rebuild.

### Scenario D: Competing Paths
Adjust `REINFORCEMENT` to 0.3 on one node → that path should attract more traffic over time.

---

## Reading the Output

```
[PHEROMONE] ↑ Reinforced port 10001: 1.100   ← successful delivery
[PHEROMONE] 💨 Decayed all paths (factor=0.9) ← evaporation cycle
[PHEROMONE] ↓ Penalized port 10002: 0.850    ← failed delivery
[NODE 10000] ✓ Sent: 'Hello' → port 10001    ← message delivered
[NODE 10000] ✗ Failed to reach port 10002    ← peer down
```

---

## Stopping
Press `Ctrl+C` in each terminal.
