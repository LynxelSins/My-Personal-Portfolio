import socket
import time
from config import BROADCAST_IP, PORT
from utils.message import format_message

# discovery/announcer.py

def start_announcing(node_name, service_name="GENERIC_SERVICE"): # เพิ่ม service_name ตรงนี้
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print(f"[ANNOUNCER] Starting service: {node_name} ({service_name})")
    try:
        while True:
            # ส่งทั้ง node_name และ service_name ไปในฟังก์ชัน format_message
            msg = format_message(node_name, service_name) 
            sock.sendto(msg, (BROADCAST_IP, PORT))
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[ANNOUNCER] Stopping...")
        sock.close()