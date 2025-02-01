# global_config.py

# A mutable dictionary holding configuration (e.g., sensor ranges) for each room.
global_config = {}

# A set holding the names of active simulators.
active_simulators = set()

# A dictionary holding simulator thread information for each room.
# Each key will map to a dict with keys like 'ranges', 'stop_event', and 'thread'.
simulator_threads = {}
