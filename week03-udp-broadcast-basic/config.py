import socket

def get_network_configs():
    # สร้าง socket ชั่วคราวเพื่อหา Local IP ที่ใช้งานอยู่จริง
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # ไม่จำเป็นต้องเชื่อมต่อจริง แค่ใช้หา interface ที่ออกอินเทอร์เน็ตได้
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()

    # แยกเอา 3 ชุดแรกมาเพื่อทำ Broadcast IP (กรณี Subnet 255.255.255.0)
    # เช่น 192.168.1.5 -> 192.168.1.255
    ip_parts = local_ip.split('.')
    ip_parts[-1] = '255'
    broadcast_ip = '.'.join(ip_parts)
    
    return local_ip, broadcast_ip

# ตั้งค่าเริ่มต้น
LOCAL_IP = "10.229.104.207"
BROADCAST_IP = "255.255.255.255"
PORT = 7000
BUFFER_SIZE = 1024