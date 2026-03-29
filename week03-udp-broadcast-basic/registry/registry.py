import time
import os

class ServiceRegistry:
    def __init__(self, timeout=15):
        self.services = {} 
        self.timeout = timeout

    def update_node(self, node_id, platform, service):
        self.services[node_id] = {
            "platform": platform,
            "service": service,
            "last_seen": time.time()
        }

    def remove_stale(self):
        current_time = time.time()
        stale_nodes = [id for id, info in self.services.items() 
                       if current_time - info['last_seen'] > self.timeout]
        for node_id in stale_nodes:
            del self.services[node_id]

    def display_active_services(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{'NODE ID':<15} | {'PLATFORM':<10} | {'SERVICE':<12} | {'LAST SEEN'}")
        print("-" * 60)
        
        for node_id, info in self.services.items():
            elapsed = int(time.time() - info['last_seen'])
            print(f"{node_id:<15} | {info['platform']:<10} | {info['service']:<12} | {elapsed}s ago")