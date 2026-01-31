# ADOH DPS Simulator

A web-based damage-per-second (DPS) simulator for ADOH (A Dawn of Heroes), a popular NWN:EE server. This tool simulates attack sequences, weapon damage, critical hits, and various character buffs/feats to provide comprehensive damage analysis.

## Features

- **Realistic Simulation**: Simulates D20 attack rolls, hit calculations, and damage aggregation
- **Weapon Support**: Extensive ADOH-based weapon database with base and unique weapon properties
- **Critical Hit Mechanics**: Accurate modeling of threat ranges, confirmation rolls, and critical multipliers
- **Character Customization**: Dual-wield penalties, feats, buffs, and legendary weapon effects
- **Interactive UI**: Built with Dash and Plotly for friendly configuration and results visualizations
- **Convergence Tracking**: Ensures simulation stability with rolling window standard deviation checks

## Installation

### Prerequisites
- Python 3.12 or higher

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/adoh-dps-simulator.git
cd adoh-dps-simulator

# Install dependencies
pip install -r requirements.txt

# Install pytest for testing (optional)
pip install pytest
```

## Usage

### Running the Application
```bash
python app.py
```
The application will start on `http://127.0.0.1:8050`. Open this URL in your web browser to access the simulator.

### Running Tests
```bash
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
