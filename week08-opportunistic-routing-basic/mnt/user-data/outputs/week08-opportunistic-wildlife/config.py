# config.py — Wildlife Tracking Network (Advanced Lab)
HOST = "127.0.0.1"
BASE_PORT = 9100           # Starting port for this node
PEER_PORTS = [9101, 9102]  # Other animal/sensor nodes
BUFFER_SIZE = 2048

# Opportunistic routing settings
FORWARD_THRESHOLD = 0.4    # Lower threshold for wildlife (more opportunistic)
UPDATE_INTERVAL = 3        # seconds between forwarding attempts

# Encounter simulator settings
ENCOUNTER_INTERVAL = 5     # seconds between simulated encounters
ENCOUNTER_PROB_MIN = 0.1   # minimum encounter probability
ENCOUNTER_PROB_MAX = 0.9   # maximum encounter probability

# Message TTL (Extension B)
MESSAGE_TTL = 60           # seconds before a message expires

# Logging
LOG_FILE = "wildlife_network.log"
