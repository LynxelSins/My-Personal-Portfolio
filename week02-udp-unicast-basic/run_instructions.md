# Run Instructions — Week 02 UDP Unicast

## Prerequisites
- Python 3.x installed
- Two PowerShell terminals open in the `week02-udp-unicast-basic` folder

---

## Basic Lab

### Terminal 1 — Receiver (start first!)
```powershell
python receiver.py
```

### Terminal 2 — Sender
```powershell
python sender.py
```

---

## Extension A: Sequence Numbers

### Terminal 1
```powershell
python ext_a_receiver_seq.py
```

### Terminal 2
```powershell
python ext_a_sender_seq.py
```

---

## Extension B: Manual ACK (Retry)

### Terminal 1
```powershell
python ext_b_receiver_ack.py
```

### Terminal 2
```powershell
python ext_b_sender_ack.py
```

---

## Extension C: Rate Control

### Terminal 1
```powershell
python ext_c_receiver_rate.py
```

### Terminal 2
```powershell
python ext_c_sender_rate.py
```
Press Ctrl+C on Terminal 1 after sender finishes to see drop report.

---

## Test: Prove UDP is Unreliable

1. Do NOT start receiver.py
2. Run sender.py anyway
3. Sender exits with no error — message silently lost. ✓
