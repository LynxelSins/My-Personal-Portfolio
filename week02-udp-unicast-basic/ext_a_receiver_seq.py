"""
Extension A: Sequence Numbers
Detect lost or duplicate datagrams by tagging each message with an ID.
"""
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[RECEIVER-A] Listening on {HOST}:{PORT} (Sequence mode)")
print("[RECEIVER-A] Waiting for datagrams... (Ctrl+C to stop)\n")

received_ids = set()
expected_id = 0

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        raw = data.decode()

        # Expect format: "ID|message"
        if '|' not in raw:
            print(f"[RECEIVER-A] Bad format from {addr}: {raw}")
            continue

        msg_id_str, text = raw.split('|', 1)
        msg_id = int(msg_id_str)

        if msg_id in received_ids:
            print(f"[RECEIVER-A] ⚠ DUPLICATE  seq={msg_id} | {text}")
        else:
            if msg_id != expected_id:
                print(f"[RECEIVER-A] ⚠ MISSING    seq {expected_id}–{msg_id - 1} lost!")
            received_ids.add(msg_id)
            expected_id = msg_id + 1
            print(f"[RECEIVER-A] ✓ RECEIVED   seq={msg_id} | {text}")

    except KeyboardInterrupt:
        print(f"\n[RECEIVER-A] Done. Total received: {len(received_ids)}")
        break

sock.close()
