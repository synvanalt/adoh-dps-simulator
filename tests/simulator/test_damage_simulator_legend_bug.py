import pytest
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config


def test_heavy_flail_common_damage_format():
    """Test that Heavy Flail's common damage format is handled correctly.

    This was causing: TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    because legend_dmg_common was [0, 0, 5, 'physical'] and code tried to pop index 2.
    """
    cfg = Config()
    cfg.ROUNDS = 100
    cfg.AB = 70
    cfg.TARGET_AC = 60

    # This should not crash
    sim = DamageSimulator('Heavy Flail', cfg)
    result = sim.simulate_dps()

    # Basic validation
    assert result['dps_crits'] >= 0
    assert result['dps_no_crits'] >= 0
