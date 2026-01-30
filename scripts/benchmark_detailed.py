"""Detailed benchmark showing performance across different weapon types."""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulator.damage_simulator import DamageSimulator
from simulator.config import Config

weapons = ['Spear', 'Greataxe', 'Heavy Flail', 'Scythe', 'Halberd']
results = []

print("=" * 60)
print("PERFORMANCE BENCHMARK - Damage Dictionary Caching")
print("=" * 60)
print(f"Configuration: {10000} rounds per weapon\n")

for weapon in weapons:
    cfg = Config()
    cfg.ROUNDS = 10000

    start = time.time()
    sim = DamageSimulator(weapon, cfg)
    result = sim.simulate_dps()
    end = time.time()

    elapsed = end - start
    results.append({
        'weapon': weapon,
        'time': elapsed,
        'dps': result['dps_crits'],
    })

    print(f"{weapon:12} | Time: {elapsed:5.2f}s | DPS: {result['dps_crits']:6.2f}")

print("\n" + "=" * 60)
avg_time = sum(r['time'] for r in results) / len(results)
print(f"Average simulation time: {avg_time:.2f} seconds")
print("=" * 60)
