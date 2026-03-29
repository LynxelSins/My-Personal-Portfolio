# Run Instructions — Week 08 Basic Lab

## Prerequisites
- Python 3.8+
- No external libraries required (uses standard library only)

---

## Running the Lab

### Step 1: Open 3 separate terminals

### Step 2: Configure each node
Before running, set `BASE_PORT` and `PEER_PORTS` in `config.py` for each terminal:

| Terminal | BASE_PORT | PEER_PORTS     |
|----------|-----------|----------------|
| 1        | 9000      | [9001, 9002]   |
| 2        | 9001      | [9000, 9002]   |
| 3        | 9002      | [9000, 9001]   |

> **Tip:** You can also copy `config.py` to `config_9001.py` etc. and import the right one,
> or pass the port as a command-line argument if you extend `node.py`.

### Step 3: Start each node
```bash
python node.py
```

### Step 4: Observe the output
- Nodes attempt to send messages on startup
- Failed deliveries are queued
- Every 5 seconds, queued messages are retried
- Adjust probabilities in code to see threshold effects

---

## Testing Scenarios

### Scenario A: All peers online
Start all 3 nodes → messages should deliver immediately.

### Scenario B: Peer unavailable
Start only node 9000, then after 10s start node 9001.
→ Node 9000 queues messages → delivers when 9001 comes online.

### Scenario C: Threshold filtering
Set one peer's probability to 0.3 (below threshold) and another to 0.7.
→ Only the peer with 0.7 should receive the message.

---

## Stopping
Press `Ctrl+C` in each terminal.
