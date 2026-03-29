# config.py — Self-Healing Network (Advanced Lab)
HOST = "127.0.0.1"
BASE_PORT = 10100
PEER_PORTS = [10101, 10102]
BUFFER_SIZE = 2048

# Pheromone parameters
INITIAL_PHEROMONE = 1.0
DECAY_FACTOR = 0.85          # Faster decay for more dynamic self-healing
REINFORCEMENT = 0.2          # Stronger reinforcement for adaptive learning
PENALTY = 0.15               # Penalty on failed delivery
FORWARD_THRESHOLD = 0.15     # Low threshold — try to find any viable path

# Timing
UPDATE_INTERVAL = 4          # seconds between forwarding cycles
FAILURE_SIMULATION_INTERVAL = 20  # seconds between simulated link failures

# Multi-flow simulation
NUM_FLOWS = 3                # Number of simultaneous message flows

# Logging
LOG_FILE = "bio_network.log"
