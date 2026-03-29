import socket
import json
from config import PORT, BUFFER_SIZE
from registry.registry import ServiceRegistry

def start_discovery():
    registry = ServiceRegistry()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    sock.settimeout(1.0) 

    print(f"[DISCOVERY] Listening on port {PORT}...")
    
    while True:
        try:
            # ส่วนนี้ต้องอยู่ใน loop ของฟังก์ชันนี้เท่านั้น
            data, addr = sock.recvfrom(BUFFER_SIZE)
            msg = json.loads(data.decode())
            
            # อัปเดตข้อมูลลงสมอง (Registry)
            registry.update_node(msg['node_id'], msg['platform'], msg['service'])
            
        except (socket.timeout, json.JSONDecodeError, KeyError):
            pass 
            
        registry.remove_stale() # ลบเครื่องที่หายไป
        registry.display_active_services() # แสดงผลหน้าจอ