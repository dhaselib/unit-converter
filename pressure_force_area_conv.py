PRESSURE_FACTORS = {
    'Pa': 1.0,
    'N/m2': 1.0,
    'kPa': 1000.0,
    'MPa': 1e6,
    'GPa': 1e9,
    'bar': 100000.0,
    'mH2O': 9806.65,
    'psi': 6894.757293168361,
    'psf': 47.88025898033584,
    'ksi': 6894757.293168361,
    'atm': 101325.0,
}
FORCE_FACTORS = {
    'N': 1.0,
    'kN': 1000.0,
    'MN': 1e6,
    'GN': 1e9,
    'kgf': 9.80665,
    'lbf': 4.4482216152605,
    'kip': 4448.2216152605,
}
AREA_FACTORS = {
    'mm2': 1e-6,
    'cm2': 1e-4,
    'dm2': 1e-2,
    'm2': 1.0,
    'ha': 10000.0,
    'km2': 1e6,
    'in2': 0.00064516,
    'ft2': 0.09290304,
    'yd2': 0.83612736,
    'ac': 4046.8564224,
    'mi2': 2589988.110336,
}
def convert_pressure_force_area(to_u, from_u):
    for dct in [PRESSURE_FACTORS, FORCE_FACTORS, AREA_FACTORS]:
        if to_u in dct and from_u in dct:
            return dct[from_u] / dct[to_u], 0.0
    return None, None
