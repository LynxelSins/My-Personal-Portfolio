# Run Instructions — Week 10 Basic Lab

## Prerequisites
- Python 3.8+
- Standard library only — no pip installs required

---

## Running the Lab

### Step 1: Open 3 separate terminals

### Step 2: Set port configuration per terminal

| Terminal | BASE_PORT | PEER_PORTS       |
|----------|-----------|------------------|
| 1        | 11000     | [11001, 11002]   |
| 2        | 11001     | [11000, 11002]   |
| 3        | 11002     | [11000, 11001]   |

Edit `config.py` before each run.

### Step 3: Start each node
```bash
python node.py
```

---

## Test Scenarios

### Scenario A: Normal Token Delivery
Start all 3 nodes → observe token created, sent, consumed exactly once.

### Scenario B: Double-Read Attempt
After a token is consumed, manually call `token.read_token()` again in the Python REPL.
Expected: returns `None` with "Already consumed" message.

### Scenario C: Token Expiry
Set `TOKEN_EXPIRY = 3` in config.py.
Start a node but do NOT start its peer.
Wait 3+ seconds → token expires before delivery.
Expected: purge cycle removes the expired token from queue.

### Scenario D: No-Cloning Verification
Observe the `break` in `forward_loop()` after a successful send.
Remove it and see what happens — the token reaches multiple peers.
Then restore it to enforce the no-cloning rule.

---

## Token State Machine

```
Created (unread)
     │
     ├──── read_token() called within expiry → CONSUMED ──→ None on retry
     │
     └──── expiry exceeded ─────────────────→ EXPIRED  ──→ None on read
```

---

## Stopping
Press `Ctrl+C` in each terminal.
