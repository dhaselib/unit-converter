import math
SPEED_FACTORS = {
    'm/s': 1.0,
    'km/h': 1.0 / 3.6,
    'km/s': 1000.0,
    'ft/s': 0.3048,
    'kn': 0.5144444444444444,
}
ACCEL_FACTORS = {'m/s2': 1.0, 'cm/s2': 0.01, 'ft/s2': 0.3048}
DATA_FACTORS = {
    'bit': 0.125,
    'B': 1.0,
    'kB': 1000.0,
    'MB': 1e6,
    'GB': 1e9,
    'TB': 1e12,
    'KiB': 1024.0,
    'MiB': 1048576.0,
    'GiB': 1073741824.0,
    'TiB': 1099511627776.0,
}
FREQ_FACTORS = {
    'ÂµHz': 1e-6,
    'mHz': 1e-3,
    'Hz': 1.0,
    'kHz': 1e3,
    'MHz': 1e6,
    'GHz': 1e9,
    'THz': 1e12,
    'rpm': 1 / 60.0,
    'VPM': 1 / 60.0,
}
VOLTAGE_FACTORS = {'V': 1.0, 'kV': 1000.0, 'MV': 1e6, 'GV': 1e9}
ANGLE_FACTORS = {
    'rad': 1.0,
    'Â°': math.pi / 180.0,
    'gon': math.pi / 200.0,
    'mgon': math.pi / 200000.0,
}
CO2_FACTORS = {'tCO2e': 1.0, 'kgCO2e': 0.001, 'lbCO2e': 0.00045359237}
THERMAL_INSULANCE_FACTORS = {
    'K.m2/W': 1.0,
    'm2.K/W': 1.0,
    'h.ft2.Â°F/BTU': 0.17611018368230588,
    'ft2.h.Â°F/BTU': 0.17611018368230588,
}
def convert_misc(to_u, from_u):
    if to_u == 'N/(m/s)' and from_u == 'lbf/(ft/s)':
        return 4.4482216152605 / 0.3048, 0.0
    if to_u in THERMAL_INSULANCE_FACTORS and from_u in THERMAL_INSULANCE_FACTORS:
        return THERMAL_INSULANCE_FACTORS[from_u] / THERMAL_INSULANCE_FACTORS[to_u], 0.0
    for dct in [SPEED_FACTORS, ACCEL_FACTORS, DATA_FACTORS, FREQ_FACTORS, VOLTAGE_FACTORS, ANGLE_FACTORS, CO2_FACTORS]:
        if to_u in dct and from_u in dct:
            return dct[from_u] / dct[to_u], 0.0
    if to_u in ['head', 'hab'] and from_u in ['head', 'hab', 'inhabitant']:
        return 1.0, 0.0
    if to_u == 'head' and from_u == 'million hab':
        return 1e6, 0.0
    if to_u == 'Bel' and from_u == 'dB':
        return 0.1, 0.0
    return None, None
