import json
import platform

def format_message(node_id, service_type, status="ONLINE"):
    return json.dumps({
        "node_id": node_id,
        "platform": platform.system(), 
        "service": service_type,
        "status": status
    }).encode()
