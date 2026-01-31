import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulator.damage_simulator import DamageSimulator
from simulator.config import Config

cfg = Config()
cfg.ROUNDS = 10000

start = time.time()
sim = DamageSimulator('Spear', cfg)
results = sim.simulate_dps()
end = time.time()

print(f"Simulation completed in {end - start:.2f} seconds")
print(f"DPS: {results['dps_crits']:.2f}")
