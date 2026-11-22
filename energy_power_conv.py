ENERGY_FACTORS = {
    'J': 1.0,
    'kJ': 1e3,
    'MJ': 1e6,
    'GJ': 1e9,
    'Wh': 3600.0,
    'kWh': 3.6e6,
    'MWh': 3.6e9,
    'GWh': 3.6e12,
    'cal': 4.1868,
    'BTU': 1055.05585262,
    'ft.lbf': 1.3558179483314004,
    'toe': 41868000000.0,
    'tce': 29307600000.0,
    'boe': 6117863200.0,
}
POWER_FACTORS = {
    'W': 1.0,
    'kW': 1e3,
    'MW': 1e6,
    'GW': 1e9,
    'TW': 1e12,
    'hp': 745.6998715822702,
    'cv': 735.49875,
    'BTU/h': 0.29307107,
}
def convert_energy_power(to_u, from_u):
    if to_u in ENERGY_FACTORS and from_u in ENERGY_FACTORS:
        return ENERGY_FACTORS[from_u] / ENERGY_FACTORS[to_u], 0.0
    if to_u in POWER_FACTORS and from_u in POWER_FACTORS:
        return POWER_FACTORS[from_u] / POWER_FACTORS[to_u], 0.0
    return None, None
