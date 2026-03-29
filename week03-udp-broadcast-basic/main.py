import sys
from discovery.announcer import start_announcing
from discovery.responder import start_discovery

from config import LOCAL_IP

def main():
    # ตรวจสอบว่ามีการส่ง Argument มาไหม เช่น: python main.py announce MyTablet
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "announce":
            name = sys.argv[2] if len(sys.argv) > 2 else "Unknown-Node"
            print(f"Running on {LOCAL_IP}")
            start_announcing(name, "GENERIC_SERVICE")
        elif mode == "listen":
            start_discovery()
    else:
        # ถ้าไม่ส่งอะไรมาเลย ให้แสดงเมนูเหมือนเดิม
        print(f"Your IP: {LOCAL_IP}")
        print("Usage: python main.py [announce|listen] [device_name]")

if __name__ == "__main__":
    main()