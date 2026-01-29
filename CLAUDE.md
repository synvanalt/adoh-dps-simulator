### Architecture at a Glance

- **simulator/**: Core calculation engine (config.py, weapon.py, attack_simulator.py, damage_simulator.py)
- **components/**: Modular Dash UI sections
- **callbacks/**: Input/output handlers (core_, ui_, plots_, validation_)
- **app.py**: Main Dash application entry point
- **weapons_db.py**: Weapon property definitions
- **tests/**: Pytest suite (all tests must pass)
