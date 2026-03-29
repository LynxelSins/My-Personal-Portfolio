# Run Instructions — Week 04 UDP Multicast

## Prerequisites
- Python 3.x installed
- Open multiple PowerShell terminals in `week04-udp-multicast-basic` folder
- **Always start receiver(s) BEFORE sender**

---

## Basic Lab

### Terminal 1 — Receiver (join group first!)
```powershell
python receiver.py
```

### Terminal 2 — Sender
```powershell
python sender.py
```

---

## Test 2: Multiple Receivers, One Sender

```powershell
# Terminal 1
python receiver.py

# Terminal 2
python receiver.py

# Terminal 3
python receiver.py

# Terminal 4 — send once, all 3 receivers get it
python sender.py
```

---

## Test 3: Non-Member Selectivity Proof

```powershell
# Terminal 1 — receiver WITHOUT joining
python receiver_no_join.py

# Terminal 2 — send multicast
python sender.py
# receiver_no_join gets nothing!
```

---

## Extension A: Periodic Stream

```powershell
# Terminal 1 (or more)
python receiver.py

# Terminal 2
python ext_a_sender_stream.py
# Ctrl+C on either terminal to stop
```

---

## Extension B: Multiple Groups

```powershell
# Terminal 1 — joins all 3 channels
python ext_b_receiver_multigroup.py

# Terminal 2 — sends to all 3 groups
python ext_b_sender_multigroup.py
```

---

## Extension C: Dynamic Join/Leave

```powershell
# Terminal 1 — run streaming sender first
python ext_a_sender_stream.py

# Terminal 2 — joins, receives 15s, then leaves
python ext_c_receiver_dynamic.py
# Watch messages stop after "LEFT group" message
```

---

## TTL Reference

| TTL | Scope |
|-----|-------|
| 1   | Local LAN only (safe for testing) |
| 32  | Campus / building |
| 255 | Internet-wide |

Change TTL in `config.py`. Always use TTL=1 for lab testing.
