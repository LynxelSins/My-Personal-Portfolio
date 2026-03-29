# config.py
HOST = "127.0.0.1"
BASE_PORT = 10000
PEER_PORTS = [10001, 10002]  # Example peers
BUFFER_SIZE = 1024
INITIAL_PHEROMONE = 1.0
DECAY_FACTOR = 0.9           # Pheromone evaporation rate per cycle
REINFORCEMENT = 0.1          # Pheromone added on successful delivery
FORWARD_THRESHOLD = 0.2      # Minimum pheromone to consider a path
UPDATE_INTERVAL = 5          # seconds between forwarding cycles
